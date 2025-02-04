"""
# SPDX-License-Identifier: Apache-2.0
Job Service

Provides business logic for job execution and management.
"""

from typing import Any, Dict
from uuid import UUID

from graphcap.dag import DAG, NODE_TYPES
from loguru import logger

from .manager import JobManager
from .schemas import PipelineConfig


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
        # Mark job as started
        await job_manager.start_job(job_id)
        logger.info(f"Starting pipeline execution for job {job_id}")

        # Create and validate DAG
        dag = DAG.from_dict(config.dict()["config"], node_classes=NODE_TYPES)
        dag.validate()
        logger.info(f"DAG validated successfully for job {job_id}")

        # Execute DAG with optional start node
        results = await dag.execute(start_node=config.start_node)
        logger.info(f"DAG execution completed for job {job_id}")

        # Process results
        processed_results = process_dag_results(results)
        await job_manager.complete_job(job_id, processed_results)
        logger.info(f"Job {job_id} completed successfully")

    except Exception as e:
        logger.error(f"Pipeline execution failed for job {job_id}: {e}")
        await job_manager.fail_job(job_id, str(e))
        raise


def process_dag_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process DAG execution results into a format suitable for storage.

    Args:
        results: Raw DAG execution results

    Returns:
        Processed results dictionary
    """
    processed: Dict[str, Any] = {
        "node_results": {},
        "outputs": {},
        "metadata": {
            "completed_nodes": list(results.keys()),
            "has_errors": False,
        },
    }

    for node_id, node_result in results.items():
        # Store full result under node_results
        processed["node_results"][node_id] = node_result

        # If node produced output files, store their paths
        if isinstance(node_result, dict):
            if "output_paths" in node_result:
                processed["outputs"][node_id] = node_result["output_paths"]
            elif "visualization" in node_result:
                processed["outputs"][node_id] = node_result["visualization"]

    return processed
