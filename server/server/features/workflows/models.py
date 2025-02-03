"""
# SPDX-License-Identifier: Apache-2.0
Workflow Models

SQLAlchemy models for workflow management.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from server.db import Base
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column


class JobStatus(str, Enum):
    """Job status enum."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineJob(Base):
    """Pipeline job model."""

    __tablename__ = "pipeline_jobs"

    id: Mapped[UUID] = mapped_column(PgUUID, primary_key=True, default=uuid4)
    pipeline_id: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[JobStatus] = mapped_column(SQLAEnum(JobStatus))
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    results: Mapped[Optional[dict]] = mapped_column(JSONB)
    job_metadata: Mapped[Optional[dict]] = mapped_column(JSONB)


class PipelineNodeState(Base):
    """Pipeline node state model."""

    __tablename__ = "pipeline_node_states"

    id: Mapped[UUID] = mapped_column(PgUUID, primary_key=True, default=uuid4)
    job_id: Mapped[UUID] = mapped_column(ForeignKey("pipeline_jobs.id"), nullable=False)
    node_id: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[JobStatus] = mapped_column(SQLAEnum(JobStatus))
    result: Mapped[Optional[dict]] = mapped_column(JSONB)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class Workflow(Base):
    """Workflow model for storing DAG configurations."""

    __tablename__ = "workflows"

    id: Mapped[UUID] = mapped_column(PgUUID, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
