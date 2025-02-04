"""
# SPDX-License-Identifier: Apache-2.0
Workflow Schemas

Pydantic models for workflow validation and serialization.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class WorkflowMetadata(BaseModel):
    """Workflow metadata schema."""

    name: str
    description: str | None = None
    version: str


class WorkflowBase(BaseModel):
    """Base workflow schema."""

    name: str
    description: str | None = None
    config: dict[str, Any]
    workflow_metadata: WorkflowMetadata | None = None
    file_hash: str | None = None  # Add file hash field


class WorkflowCreate(WorkflowBase):
    """Workflow creation schema."""

    pass


class Workflow(WorkflowBase):
    """Complete workflow schema."""

    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class WorkflowResponse(BaseModel):
    """Workflow response model."""

    id: UUID
    name: str
    description: Optional[str] = None
    config: dict
    workflow_metadata: Optional[WorkflowMetadata] = None


class WorkflowUpdate(BaseModel):
    """Workflow update model."""

    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[dict] = None
    workflow_metadata: Optional[WorkflowMetadata] = None
