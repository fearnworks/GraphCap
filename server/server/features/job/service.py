"""
# SPDX-License-Identifier: Apache-2.0
Job Service

Provides business logic for job execution and management.
"""

from uuid import UUID

from graphcap.dag import DAG, NODE_TYPES
from loguru import logger

from .schemas import PipelineConfig


async def execute_pipeline(
    job_id: UUID,
    config: PipelineConfig,
    job_manager,
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
