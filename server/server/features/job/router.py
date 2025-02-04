"""
# SPDX-License-Identifier: Apache-2.0
Job Router

Handles pipeline execution and job management endpoints.
"""

import asyncio
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from .dependencies import get_job_manager
from .schemas import JobResponse, JobStatusResponse, PipelineConfig
from .service import execute_pipeline

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/{pipeline_id}/run", response_model=JobResponse)
async def run_pipeline(
    pipeline_id: str,
    config: PipelineConfig,
    job_manager=Depends(get_job_manager),
) -> JobResponse:
    """
    Start a pipeline execution.

    Args:
        pipeline_id: Unique identifier for the pipeline
        config: Pipeline configuration
        job_manager: Job manager instance

    Returns:
        Job creation response with job ID and status
    """
    try:
        # Create job record
        job_id = await job_manager.create_job(pipeline_id, config.dict())

        # Start async execution
        asyncio.create_task(execute_pipeline(job_id, config, job_manager))

        return JobResponse(
            job_id=job_id,
            pipeline_id=pipeline_id,
            status="PENDING",
        )

    except Exception as e:
        logger.error(f"Failed to start pipeline {pipeline_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{pipeline_id}/job/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    pipeline_id: str,
    job_id: UUID,
    job_manager=Depends(get_job_manager),
) -> JobStatusResponse:
    """
    Get job status and results.

    Args:
        pipeline_id: Pipeline identifier
        job_id: Job identifier
        job_manager: Job manager instance

    Returns:
        Job status and results
    """
    job_state = await job_manager.get_job_state(job_id)
    if not job_state:
        raise HTTPException(status_code=404, detail="Job not found")

    return job_state.model_dump()


@router.post("/{pipeline_id}/job/{job_id}/cancel")
async def cancel_job(
    pipeline_id: str,
    job_id: UUID,
    job_manager=Depends(get_job_manager),
) -> dict[str, str]:
    """
    Cancel a running job.

    Args:
        pipeline_id: Pipeline identifier
        job_id: Job identifier
        job_manager: Job manager instance

    Returns:
        Cancellation status
    """
    job_state = await job_manager.get_job_state(job_id)
    if not job_state:
        raise HTTPException(status_code=404, detail="Job not found")

    if job_state.status not in ["PENDING", "RUNNING"]:
        raise HTTPException(status_code=400, detail="Job cannot be cancelled")

    await job_manager.fail_job(job_id, "Job cancelled by user")
    return {"status": "cancelled"}
