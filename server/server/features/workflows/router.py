"""
# SPDX-License-Identifier: Apache-2.0
Workflow Router

Handles workflow CRUD operations.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from server.db import get_session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Workflow
from .schemas import WorkflowCreate, WorkflowResponse

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
