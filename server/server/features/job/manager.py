"""
# SPDX-License-Identifier: Apache-2.0
Job Manager

Handles job state management and persistence using SQLAlchemy ORM.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import JobStatus, PipelineJob, PipelineNodeState


class JobManager:
    """Manages pipeline job state and persistence."""

    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session

    async def create_job(self, pipeline_id: str, config: dict[str, Any]) -> UUID:
        """Create a new pipeline job."""
        job = PipelineJob(
            pipeline_id=pipeline_id,
            status=JobStatus.PENDING,
            config=config,
        )
        self.session.add(job)
        await self.session.commit()
        logger.info(f"Created job {job.id} for pipeline {pipeline_id}")
        return job.id

    async def get_job_state(self, job_id: UUID) -> Optional[PipelineJob]:
        """Get job state by ID."""
        result = await self.session.execute(select(PipelineJob).where(PipelineJob.id == job_id))
        return result.scalar_one_or_none()

    async def start_job(self, job_id: UUID) -> None:
        """Mark job as started."""
        job = await self.get_job_state(job_id)
        if job:
            job.status = JobStatus.RUNNING
            job.started_at = datetime.utcnow()
            await self.session.commit()
            logger.info(f"Started job {job_id}")

    async def complete_job(self, job_id: UUID, results: dict[str, Any]) -> None:
        """Mark job as completed with results."""
        job = await self.get_job_state(job_id)
        if job:
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.results = results
            await self.session.commit()
            logger.info(f"Completed job {job_id}")

    async def fail_job(self, job_id: UUID, error: str) -> None:
        """Mark job as failed with error."""
        job = await self.get_job_state(job_id)
        if job:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.utcnow()
            job.error_message = error
            await self.session.commit()
            logger.error(f"Failed job {job_id}: {error}")

    async def update_node_state(
        self,
        job_id: UUID,
        node_id: str,
        status: str,
        result: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        """Update individual node execution state."""
        job = await self.get_job_state(job_id)
        if job:
            node_state = PipelineNodeState(
                job_id=job_id,
                node_id=node_id,
                status=status,
                result=result,
                error_message=error,
                started_at=datetime.utcnow(),
            )
            self.session.add(node_state)
            await self.session.commit()
            logger.info(f"Updated node {node_id} state for job {job_id}: {status}")
