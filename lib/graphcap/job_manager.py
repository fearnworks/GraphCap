"""
# SPDX-License-Identifier: Apache-2.0
Job Manager for Pipeline Execution

Handles job queuing, status tracking, and result persistence using PostgreSQL.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

import asyncpg
from pydantic import BaseModel


class JobState(BaseModel):
    """Job state and metadata."""

    id: UUID
    pipeline_id: str
    status: str
    config: Dict[str, Any]
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class JobManager:
    """Manages pipeline job execution and state."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create_job(self, pipeline_id: str, config: Dict[str, Any]) -> UUID:
        """Create a new pipeline job."""
        async with self.pool.acquire() as conn:
            job_id = await conn.fetchval(
                """
                INSERT INTO pipeline_jobs (pipeline_id, config)
                VALUES ($1, $2)
                RETURNING id
                """,
                pipeline_id,
                config,
            )
            return job_id

    async def start_job(self, job_id: UUID) -> None:
        """Mark job as started."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE pipeline_jobs
                SET status = 'running', started_at = NOW()
                WHERE id = $1
                """,
                job_id,
            )

    async def complete_job(self, job_id: UUID, results: Dict[str, Any]) -> None:
        """Mark job as completed with results."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE pipeline_jobs
                SET status = 'completed',
                    completed_at = NOW(),
                    results = $2
                WHERE id = $1
                """,
                job_id,
                results,
            )

    async def fail_job(self, job_id: UUID, error: str) -> None:
        """Mark job as failed with error message."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE pipeline_jobs
                SET status = 'failed',
                    completed_at = NOW(),
                    error_message = $2
                WHERE id = $1
                """,
                job_id,
                error,
            )

    async def get_job_state(self, job_id: UUID) -> Optional[JobState]:
        """Get current job state."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM pipeline_jobs WHERE id = $1
                """,
                job_id,
            )
            return JobState(**dict(row)) if row else None

    async def update_node_state(
        self,
        job_id: UUID,
        node_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        """Update individual node execution state."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO pipeline_node_states (
                    job_id, node_id, status, result, error_message, started_at
                )
                VALUES ($1, $2, $3, $4, $5, NOW())
                ON CONFLICT (job_id, node_id)
                DO UPDATE SET
                    status = EXCLUDED.status,
                    result = EXCLUDED.result,
                    error_message = EXCLUDED.error_message,
                    completed_at = CASE
                        WHEN EXCLUDED.status IN ('completed', 'failed')
                        THEN NOW()
                        ELSE NULL
                    END
                """,
                job_id,
                node_id,
                status,
                result,
                error,
            )
