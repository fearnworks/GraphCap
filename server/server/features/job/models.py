"""
# SPDX-License-Identifier: Apache-2.0
Job Models

SQLAlchemy models for job execution and state management.

Key features:
- Job state tracking
- Pipeline execution history
- Node-level state management
- Error tracking and results storage

Models:
    JobStatus: Status enumeration for jobs and nodes
    PipelineJob: Tracks overall pipeline execution
    PipelineNodeState: Tracks individual node execution
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from server.db import Base
from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column


class JobStatus(str, Enum):
    """
    Job status enumeration.

    Used to track the execution state of both overall jobs
    and individual pipeline nodes.

    Values:
        PENDING: Job is created but not started
        RUNNING: Job is currently executing
        COMPLETED: Job finished successfully
        FAILED: Job encountered an error
        CANCELLED: Job was manually cancelled
    """

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PipelineJob(Base):
    """
    Pipeline job execution model.

    Tracks the execution of a complete pipeline including
    configuration, results, and timing information.

    Attributes:
        id (UUID): Unique job identifier
        pipeline_id (str): Associated pipeline identifier
        status (JobStatus): Current job status
        config (dict): Pipeline configuration used
        created_at (datetime): Job creation time
        started_at (datetime): Execution start time
        completed_at (datetime): Execution end time
        error_message (str): Error details if failed
        results (dict): Execution results
        job_metadata (dict): Additional job metadata
    """

    __tablename__ = "pipeline_jobs"

    id: Mapped[UUID] = mapped_column(PgUUID, primary_key=True, default=uuid4)
    pipeline_id: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[JobStatus] = mapped_column(
        SQLAEnum(JobStatus, name="job_status", create_type=False), nullable=False, default=JobStatus.PENDING
    )
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    results: Mapped[Optional[dict]] = mapped_column(JSONB)
    job_metadata: Mapped[Optional[dict]] = mapped_column(JSONB)


class PipelineNodeState(Base):
    """
    Pipeline node execution state model.

    Tracks the execution state and results of individual
    nodes within a pipeline job.

    Attributes:
        id (UUID): Unique state identifier
        job_id (UUID): Parent job identifier
        node_id (str): Node identifier within the DAG
        status (JobStatus): Current node status
        result (dict): Node execution results
        error_message (str): Error details if failed
        started_at (datetime): Node start time
        completed_at (datetime): Node completion time
    """

    __tablename__ = "pipeline_node_states"

    id: Mapped[UUID] = mapped_column(PgUUID, primary_key=True, default=uuid4)
    job_id: Mapped[UUID] = mapped_column(ForeignKey("pipeline_jobs.id"), nullable=False)
    node_id: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[JobStatus] = mapped_column(
        SQLAEnum(JobStatus, name="job_status", create_type=False), nullable=False, default=JobStatus.PENDING
    )
    result: Mapped[Optional[dict]] = mapped_column(JSONB)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
