"""
# SPDX-License-Identifier: Apache-2.0
Workflow Schemas

Pydantic models for perspective validation and serialization.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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


class WorkflowResponse(BaseModel):
    """Workflow response model."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None = None
    config: dict[str, Any]
    workflow_metadata: WorkflowMetadata | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    file_hash: str | None = None


class WorkflowUpdate(BaseModel):
    """Workflow update model."""

    name: str | None = None
    description: str | None = None
    config: dict[str, Any] | None = None
    workflow_metadata: WorkflowMetadata | None = None


class PerspectiveResult(BaseModel):
    """Schema for perspective analysis results."""

    filename: str
    perspective_type: str = Field(..., description="Type of perspective (art, graph, etc)")
    provider: str
    model: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    parsed: dict[str, Any]
    formal_analysis: str | None = None
    error: str | None = None


class CombinedPerspectiveResult(BaseModel):
    """Schema for combined perspective results."""

    filename: str
    perspectives: dict[str, PerspectiveResult]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
