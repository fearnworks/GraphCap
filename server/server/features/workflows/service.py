"""
# SPDX-License-Identifier: Apache-2.0
Workflow Service

Provides business logic for workflow management and execution.
"""

from uuid import UUID

from fastapi import HTTPException
from loguru import logger
from server.features.job.manager import JobManager
from server.features.job.schemas import PipelineConfig
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Workflow


async def get_workflow_config(workflow_id: UUID, session: AsyncSession) -> dict:
    """
    Get workflow configuration by ID.

    Args:
        workflow_id: Workflow identifier
        session: Database session

    Returns:
        Workflow configuration dictionary

    Raises:
        HTTPException: If workflow not found
    """
    workflow = await session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow.config


async def execute_workflow(
    workflow_id: UUID,
    job_manager: JobManager,
    session: AsyncSession,
    start_node: str | None = None,
) -> UUID:
    """
    Execute a workflow as a job.

    Args:
        workflow_id: Workflow identifier
        job_manager: Job manager instance
        session: Database session
        start_node: Optional starting node

    Returns:
        Created job ID

    Raises:
        HTTPException: If workflow not found or execution fails
    """
    try:
        # Verify job manager is properly initialized
        if not job_manager or not isinstance(job_manager, JobManager):
            logger.error(
                "Job manager initialization failed",
                manager_type=type(job_manager).__name__ if job_manager else None,
                workflow_id=workflow_id,
            )
            raise HTTPException(
                status_code=503,
                detail="Job service temporarily unavailable. Please try again later.",
            )

        # Get workflow config
        workflow = await session.get(Workflow, workflow_id)
        if not workflow:
            logger.error(f"Workflow {workflow_id} not found")
            raise HTTPException(status_code=404, detail="Workflow not found")

        # Create pipeline config
        pipeline_config = PipelineConfig(config=workflow.config, start_node=start_node)

        # Create and start job
        job_id = await job_manager.create_job(str(workflow_id), pipeline_config.model_dump())
        logger.info(
            "Workflow execution started",
            workflow_id=workflow_id,
            job_id=job_id,
            start_node=start_node,
        )

        return job_id

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(
            "Workflow execution failed",
            error=str(e),
            workflow_id=workflow_id,
            start_node=start_node,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute workflow: {str(e)}",
        )
