"""
# SPDX-License-Identifier: Apache-2.0
Workflow Schemas

Pydantic models for workflow validation and serialization.
"""

from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel


class WorkflowCreate(BaseModel):
    """Schema for creating a new workflow."""

    name: str
    description: Optional[str] = None
    config: Dict


class WorkflowResponse(BaseModel):
    """Schema for workflow responses."""

    id: UUID
    name: str
    description: Optional[str]
    config: Dict
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
