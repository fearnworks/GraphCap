"""
# SPDX-License-Identifier: Apache-2.0
Workflow Router

Handles workflow CRUD operations and execution.
"""

import asyncio
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
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
    db_workflow = Workflow(**workflow.model_dump())
    session.add(db_workflow)
    await session.commit()
    await session.refresh(db_workflow)
    return db_workflow


@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(session: AsyncSession = Depends(get_session)) -> List[WorkflowResponse]:
    """List all workflows."""
    result = await session.execute(select(Workflow).order_by(Workflow.created_at.desc()))
    return result.scalars().all()


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: UUID, session: AsyncSession = Depends(get_session)) -> WorkflowResponse:
    """Get a workflow by ID."""
    workflow = await session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


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
    job_id = await execute_workflow(workflow_id, job_manager, session, start_node)

    # Start async execution
    asyncio.create_task(execute_pipeline(job_id, job_manager))

    return JobResponse(
        job_id=job_id,
        pipeline_id=str(workflow_id),
        status="PENDING",
    )
