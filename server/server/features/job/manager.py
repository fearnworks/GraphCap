"""
# SPDX-License-Identifier: Apache-2.0
Job Manager

Handles job state management and persistence using SQLAlchemy ORM.
"""

from datetime import datetime
from typing import Any, Optional, Sequence
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

            # Log detailed result structure
            logger.debug(
                "Processing job results",
                extra={
                    "job_id": str(job_id),
                    "result_keys": list(results.keys()),
                    "has_result": "result" in results,
                    "has_metadata": "metadata" in results,
                    "metadata": results.get("metadata", {}),
                },
            )

            # Ensure we have valid results
            if not results.get("result"):
                logger.warning(
                    f"Job {job_id} completed but no valid result found",
                    extra={"error": results.get("error"), "metadata": results.get("metadata", {})},
                )
                results["error_message"] = "No valid result generated"

            job.results = results
            await self.session.commit()

            logger.info(
                f"Completed job {job_id}",
                extra={
                    "perspectives": results.get("metadata", {}).get("perspectives", []),
                    "has_errors": results.get("metadata", {}).get("has_errors", True),
                    "error_message": results.get("error_message"),
                    "result_type": type(results.get("result")).__name__ if results.get("result") else None,
                },
            )

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

    async def cancel_job(self, job_id: UUID) -> None:
        """Cancel a running job."""
        job = await self.get_job_state(job_id)
        if job:
            if job.status in [JobStatus.PENDING, JobStatus.RUNNING]:
                job.status = JobStatus.CANCELLED
                job.completed_at = datetime.utcnow()
                job.error_message = "Job cancelled by user"
                await self.session.commit()
                logger.info(f"Cancelled job {job_id}")
            else:
                logger.warning(f"Cannot cancel job {job_id} in state {job.status}")

    async def get_active_jobs(self) -> Sequence[PipelineJob]:
        """Get all active (pending or running) jobs."""
        result = await self.session.execute(
            select(PipelineJob).where(PipelineJob.status.in_([JobStatus.PENDING, JobStatus.RUNNING]))
        )
        return result.scalars().all()

    async def cancel_all_jobs(self) -> dict[str, Any]:
        """
        Cancel all active jobs.

        Returns:
            Dictionary with cancellation results
        """
        active_jobs = await self.get_active_jobs()
        cancelled_count = 0
        failed_count = 0
        job_results = []

        for job in active_jobs:
            try:
                await self.cancel_job(job.id)
                cancelled_count += 1
                job_results.append({"job_id": str(job.id), "status": "cancelled"})
            except Exception as e:
                failed_count += 1
                job_results.append({"job_id": str(job.id), "status": "failed", "error": str(e)})
                logger.error(f"Failed to cancel job {job.id}: {e}")

        results = {
            "total_jobs": len(active_jobs),
            "cancelled_count": cancelled_count,
            "failed_count": failed_count,
            "job_results": job_results,
        }

        logger.info(f"Cancelled {cancelled_count} jobs, {failed_count} failed", extra={"results": results})
        return results
