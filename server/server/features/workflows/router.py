"""
# SPDX-License-Identifier: Apache-2.0
Workflow Router

Handles workflow CRUD operations and execution.
"""

import asyncio
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from server.db import get_session
from server.features.job.dependencies import get_job_manager
from server.features.job.schemas import JobResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Workflow
from .schemas import WorkflowCreate, WorkflowResponse
from .service import execute_pipeline, execute_workflow

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/", response_model=WorkflowResponse)
async def create_workflow(workflow: WorkflowCreate, session: AsyncSession = Depends(get_session)) -> WorkflowResponse:
    """Create a new workflow."""
    async with session.begin():
        db_workflow = Workflow(**workflow.model_dump())
        session.add(db_workflow)
        await session.flush()
        await session.refresh(db_workflow)
        # Convert to response model before returning
        return WorkflowResponse.model_validate(db_workflow)


@router.get("/", response_model=list[WorkflowResponse])
async def list_workflows(session: AsyncSession = Depends(get_session)) -> list[WorkflowResponse]:
    """
    List all workflows.

    Returns:
        List of workflows ordered by creation date
    """
    try:
        async with session.begin():
            stmt = select(Workflow).order_by(Workflow.created_at.desc())
            result = await session.execute(stmt)
            workflows = result.scalars().all()
            logger.debug(f"Found {len(workflows)} workflows")
            
            response_workflows = []
            for workflow in workflows:
                try:
                    # Convert each workflow and log any validation errors
                    response = WorkflowResponse.model_validate(workflow)
                    response_workflows.append(response)
                except Exception as e:
                    logger.error(
                        "Failed to validate workflow",
                        extra={
                            "workflow_id": workflow.id,
                            "workflow_name": workflow.name,
                            "error": str(e)
                        }
                    )
                    # Optionally re-raise if you want to fail the whole request
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to validate workflow {workflow.id} ({workflow.name}): {str(e)}"
                    )
            
            return response_workflows

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list workflows: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list workflows")


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: UUID, session: AsyncSession = Depends(get_session)) -> WorkflowResponse:
    """Get a workflow by ID."""
    async with session.begin():
        workflow = await session.get(Workflow, workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        # Convert to response model before returning
        return WorkflowResponse.model_validate(workflow)


@router.post("/{workflow_id}/run", response_model=JobResponse)
async def run_workflow(
    workflow_id: UUID,
    start_node: str | None = None,
    session: AsyncSession = Depends(get_session),
    job_manager=Depends(get_job_manager),
) -> JobResponse:
    """
    Run a workflow as a job.

    Args:
        workflow_id: Workflow identifier
        start_node: Optional starting node
        session: Database session
        job_manager: Job manager instance

    Returns:
        Job creation response
    """
    try:
        # Use a new session for workflow execution to avoid state conflicts
        async with session.begin():
            job_id = await execute_workflow(workflow_id, job_manager, session, start_node)

            # Create task after transaction is complete
            asyncio.create_task(execute_pipeline(job_id, job_manager))

            return JobResponse(
                job_id=job_id,
                pipeline_id=str(workflow_id),
                status="PENDING",
            )
    except Exception as e:
        logger.error(f"Failed to run workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
