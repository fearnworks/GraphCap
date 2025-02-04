"""
# SPDX-License-Identifier: Apache-2.0
Workflow Loader

Handles loading and registration of stock workflows.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Workflow
from .schemas import WorkflowCreate, WorkflowMetadata

WORKFLOW_DIR = Path("/workspace/config/workflows")


def get_file_hash(path: Path) -> str:
    """
    Calculate SHA-256 hash of file contents.

    Args:
        path: Path to file

    Returns:
        Hex digest of file hash
    """
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


async def load_workflow_file(path: Path, session: AsyncSession) -> Optional[Workflow]:
    """
    Load a workflow from a JSON file.

    Args:
        path: Path to workflow JSON file
        session: Database session

    Returns:
        Created or updated workflow, or None if error occurs
    """
    try:
        logger.info(f"Loading workflow from {path}")

        # Load workflow JSON
        workflow_data = json.loads(path.read_text())
        file_hash = get_file_hash(path)
        logger.debug(f"File hash: {file_hash}")

        # Check if workflow already exists by ID
        workflow_id = workflow_data.get("id")
        if not workflow_id:
            logger.warning(f"Workflow file {path} missing ID field, skipping")
            return None

        # Validate required config structure
        if "nodes" not in workflow_data:
            logger.error(f"Workflow file {path} missing required 'nodes' key")
            return None

        logger.debug(f"Processing workflow ID: {workflow_id}")

        # Extract metadata
        workflow_metadata = None
        if "workflow_metadata" in workflow_data:
            workflow_metadata = WorkflowMetadata(**workflow_data["workflow_metadata"])
            logger.debug(f"Extracted metadata: {workflow_metadata.model_dump_json()}")

        # Prepare config with required structure
        config = {"nodes": workflow_data["nodes"]}

        # Check if workflow exists and needs updating
        stmt = select(Workflow).where(Workflow.name == workflow_id)
        result = await session.execute(stmt)
        existing_workflow = result.scalar_one_or_none()

        if existing_workflow:
            logger.debug(f"Found existing workflow: {existing_workflow.id}")
            if getattr(existing_workflow, "file_hash", None) != file_hash:
                logger.info(f"Updating workflow {workflow_id} - file contents changed")

                # Update workflow
                update_stmt = (
                    update(Workflow)
                    .where(Workflow.name == workflow_id)
                    .values(
                        description=workflow_metadata.description if workflow_metadata else None,
                        config=config,  # Use the properly structured config
                        workflow_metadata=workflow_metadata.model_dump() if workflow_metadata else None,
                        file_hash=file_hash,
                        updated_at=func.now(),
                    )
                )
                await session.execute(update_stmt)
                await session.refresh(existing_workflow)
                logger.info(f"Updated workflow {workflow_id}")
            return existing_workflow

        # Create new workflow with properly structured config
        workflow = WorkflowCreate(
            name=workflow_id,
            description=workflow_metadata.description if workflow_metadata else None,
            config=config,  # Use the properly structured config
            workflow_metadata=workflow_metadata,
            file_hash=file_hash,
        )

        # Create new workflow with timestamps
        db_workflow = Workflow(
            **workflow.model_dump(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        logger.debug(f"Adding workflow to session: {db_workflow.name}")
        session.add(db_workflow)

        logger.debug("Flushing session...")
        await session.flush()

        logger.debug("Refreshing workflow object...")
        await session.refresh(db_workflow)

        logger.info(f"Successfully created workflow {workflow.name} with ID {db_workflow.id}")
        return db_workflow

    except Exception as e:
        logger.error(f"Failed to load workflow {path}: {e}", exc_info=True)
        raise


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

    # Load all workflow files
    workflow_files = list(WORKFLOW_DIR.glob("*.json"))
    logger.info(f"Found {len(workflow_files)} workflow files")

    for path in workflow_files:
        if path.name != "README.md":  # Skip README
            logger.debug(f"Processing file: {path.name}")
            try:
                await load_workflow_file(path, session)
            except Exception:
                logger.error(f"Failed to load workflow {path}", exc_info=True)
                continue

    try:
        logger.debug("Committing all changes...")
        await session.commit()

        # Verify workflows were loaded
        stmt = select(func.count()).select_from(Workflow)
        result = await session.execute(stmt)
        count = result.scalar()
        logger.info(f"Total workflows in database after loading: {count}")

    except Exception:
        logger.error("Failed to commit workflow changes", exc_info=True)
        await session.rollback()
        raise
