"""
# SPDX-License-Identifier: Apache-2.0
Pipeline Router

Handles pipeline execution and job management endpoints.
"""

import asyncio
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from graphcap.dag import DAG, NODE_TYPES
from graphcap.job_manager import JobManager
from loguru import logger
from pydantic import BaseModel

from ..dependencies import get_job_manager


class PipelineConfig(BaseModel):
    """Pipeline configuration model."""

    config: Dict[str, Any]
    start_node: Optional[str] = None


class JobResponse(BaseModel):
    """Job creation response model."""

    job_id: UUID
    pipeline_id: str
    status: str


router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/{pipeline_id}/run", response_model=JobResponse)
async def run_pipeline(
    pipeline_id: str,
    config: PipelineConfig,
    job_manager: JobManager = Depends(get_job_manager),
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
            status="pending",
        )

    except Exception as e:
        logger.error(f"Failed to start pipeline {pipeline_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{pipeline_id}/job/{job_id}", response_model=Dict[str, Any])
async def get_job_status(
    pipeline_id: str,
    job_id: UUID,
    job_manager: JobManager = Depends(get_job_manager),
) -> Dict[str, Any]:
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
    job_manager: JobManager = Depends(get_job_manager),
) -> Dict[str, str]:
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

    if job_state.status not in ["pending", "running"]:
        raise HTTPException(status_code=400, detail="Job cannot be cancelled")

    await job_manager.fail_job(job_id, "Job cancelled by user")
    return {"status": "cancelled"}


async def execute_pipeline(
    job_id: UUID,
    config: PipelineConfig,
    job_manager: JobManager,
) -> None:
    """
    Execute pipeline asynchronously.

    Args:
        job_id: Job identifier
        config: Pipeline configuration
        job_manager: Job manager instance
    """
    try:
        await job_manager.start_job(job_id)

        # Create and validate DAG
        dag = DAG.from_dict(config.config, node_classes=NODE_TYPES)
        dag.validate()

        # Execute DAG
        results = await dag.execute(start_node=config.start_node)

        # Update job with results
        await job_manager.complete_job(job_id, results)

    except Exception as e:
        logger.error(f"Pipeline execution failed for job {job_id}: {e}")
        await job_manager.fail_job(job_id, str(e))
