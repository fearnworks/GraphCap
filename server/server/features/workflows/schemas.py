"""
# SPDX-License-Identifier: Apache-2.0
Workflow Schemas

Pydantic models for workflow validation and serialization.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class WorkflowMetadata(BaseModel):
    """Workflow metadata model."""

    name: str = Field(..., description="Human-readable workflow name")
    description: str = Field(..., description="Workflow description")
    version: str = Field(..., description="Workflow version")


class WorkflowCreate(BaseModel):
    """Workflow creation model."""

    name: str = Field(..., description="Human-readable workflow name")
    description: Optional[str] = Field(None, description="Optional workflow description")
    config: dict = Field(..., description="DAG configuration")
    workflow_metadata: Optional[WorkflowMetadata] = Field(None, description="Optional workflow metadata")


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
