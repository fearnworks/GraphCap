"""
# SPDX-License-Identifier: Apache-2.0
Stock Workflow Loader

Loads predefined workflow configurations from JSON files.
"""

import json
from pathlib import Path

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Workflow


async def load_stock_workflows(session: AsyncSession) -> None:
    """
    Load stock workflows from configuration files.

    Args:
        session: Database session to use for loading workflows
    """
    config_dir = Path("/config/batch_configs/tests")
    logger.info(f"Looking for stock workflows in: {config_dir}")

    try:
        if not config_dir.exists():
            logger.error(f"Config directory does not exist: {config_dir}")
            return

        logger.debug(f"Directory contents: {list(config_dir.glob('*.json'))}")
        workflow_files = list(config_dir.glob("*.json"))
        logger.info(f"Found {len(workflow_files)} stock workflow files")

        for workflow_file in workflow_files:
            logger.info(f"Processing workflow file: {workflow_file}")
            try:
                # Log file existence and permissions
                logger.debug(f"File exists: {workflow_file.exists()}")
                logger.debug(f"File permissions: {oct(workflow_file.stat().st_mode)[-3:]}")

                # Try to read the file and log its size
                logger.debug(f"File size: {workflow_file.stat().st_size} bytes")

                with open(workflow_file, "r") as f:
                    logger.debug(f"Successfully opened {workflow_file}")
                    try:
                        config = json.load(f)
                        logger.debug(f"Successfully parsed JSON from {workflow_file}")
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON parsing error in {workflow_file}: {e}")
                        continue

                # Log workflow details before saving
                logger.debug(f"Attempting to save workflow: {config.get('name', 'unnamed')}")

                # Create all workflows in a batch
                workflow = Workflow(
                    name=config.get("name", workflow_file.stem),
                    description=config.get("description", ""),
                    config=config,
                )
                session.add(workflow)

            except Exception as e:
                logger.error(f"Error loading stock workflow {workflow_file}: {e}", exc_info=True)
                await session.rollback()
                continue

        # Commit all workflows at once
        await session.commit()
        logger.info("Successfully committed all workflows")

    except Exception as e:
        logger.error(f"Error in load_stock_workflows: {e}", exc_info=True)
        await session.rollback()
        raise
