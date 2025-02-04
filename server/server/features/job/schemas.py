"""
# SPDX-License-Identifier: Apache-2.0
Job Schemas

Pydantic models for job validation and serialization.
"""

from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PipelineConfig(BaseModel):
    """Pipeline configuration model."""

    config: Dict[str, Any]
    start_node: Optional[str] = Field(None, description="Starting node for pipeline execution")


class JobResponse(BaseModel):
    """Job creation response model."""

    job_id: UUID
    pipeline_id: str
    status: str


class JobStatusResponse(BaseModel):
    """Job status response model."""

    id: UUID
    pipeline_id: str
    status: str
    config: Dict[str, Any]
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
