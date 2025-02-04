"""
# SPDX-License-Identifier: Apache-2.0
Workflow Loader

Handles loading and registration of stock workflows.
"""

import json
from pathlib import Path
from typing import Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Workflow
from .schemas import WorkflowCreate, WorkflowMetadata

WORKFLOW_DIR = Path("/workspace/config/workflows")


async def load_workflow_file(path: Path, session: AsyncSession) -> Optional[Workflow]:
    """
    Load a workflow from a JSON file.

    Args:
        path: Path to workflow JSON file
        session: Database session

    Returns:
        Created workflow or None if already exists
    """
    try:
        # Load workflow JSON
        workflow_data = json.loads(path.read_text())

        # Check if workflow already exists by ID
        workflow_id = workflow_data.get("id")
        if workflow_id:
            stmt = select(Workflow).where(Workflow.name == workflow_id)
            result = await session.execute(stmt)
            if result.scalar_one_or_none():
                logger.info(f"Workflow {workflow_id} already exists, skipping")
                return None

        # Extract metadata
        workflow_metadata = None
        if "workflow_metadata" in workflow_data:
            workflow_metadata = WorkflowMetadata(**workflow_data["workflow_metadata"])

        # Create workflow using only the ID and metadata
        workflow = WorkflowCreate(
            name=workflow_id,
            description=workflow_metadata.description if workflow_metadata else None,
            config={"nodes": workflow_data["nodes"]},
            workflow_metadata=workflow_metadata,
        )

        # Save to database
        db_workflow = Workflow(**workflow.model_dump())
        session.add(db_workflow)
        await session.commit()
        await session.refresh(db_workflow)

        logger.info(f"Loaded workflow {workflow.name}")
        return db_workflow

    except Exception as e:
        logger.error(f"Failed to load workflow {path}: {e}")
        return None


async def load_stock_workflows(session: AsyncSession) -> None:
    """
    Load all stock workflows from the workflows directory.

    Args:
        session: Database session
    """
    logger.info(f"Loading stock workflows from {WORKFLOW_DIR}")

    if not WORKFLOW_DIR.exists():
        logger.warning(f"Workflow directory {WORKFLOW_DIR} does not exist")
        return

    for path in WORKFLOW_DIR.glob("*.json"):
        await load_workflow_file(path, session)
