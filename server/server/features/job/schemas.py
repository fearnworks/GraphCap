"""
# SPDX-License-Identifier: Apache-2.0
Job Schemas

Pydantic models for job validation and serialization.
"""

from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class PipelineConfig(BaseModel):
    """Pipeline configuration model."""

    config: dict[str, Any] = Field(..., description="Complete workflow configuration including nodes")
    start_node: str | None = Field(None, description="Starting node for pipeline execution")

    @field_validator("config")
    def validate_config(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Validate workflow configuration."""
        if "nodes" not in v:
            raise ValueError("Configuration must contain a 'nodes' list")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "config": {"nodes": [{"id": "node1", "type": "SomeNodeType", "config": {}, "dependencies": []}]},
                "start_node": "node1",
            }
        }
    }


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
