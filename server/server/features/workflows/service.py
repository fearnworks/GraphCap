"""
# SPDX-License-Identifier: Apache-2.0
Workflow Service

Provides business logic for workflow management and execution.
"""

from typing import Any
from uuid import UUID

from fastapi import HTTPException
from graphcap.dag import DAG
from graphcap.node_index import NODE_CLASS_MAPPINGS
from loguru import logger
from server.features.job.manager import JobManager
from server.features.job.schemas import PipelineConfig
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Workflow


async def get_workflow_config(workflow_id: UUID, session: AsyncSession) -> dict:
    """
    Get workflow configuration by ID.

    Args:
        workflow_id: Workflow identifier
        session: Database session

    Returns:
        Workflow configuration dictionary

    Raises:
        HTTPException: If workflow not found
    """
    workflow = await session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow.config


async def execute_pipeline(job_id: UUID, job_manager: JobManager) -> None:
    """
    Execute a pipeline job.

    Args:
        job_id: Job identifier
        job_manager: Job manager instance
    """
    try:
        # Get job state and config
        job = await job_manager.get_job_state(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return

        # Mark job as started
        await job_manager.start_job(job_id)
        logger.info(f"Starting pipeline execution for job {job_id}")

        # Create and validate DAG
        config = PipelineConfig(**job.config)
        dag = DAG.from_dict(config.dict()["config"], node_classes=NODE_CLASS_MAPPINGS)
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
        # Ensure session is rolled back before trying to update job status
        await job_manager.session.rollback()
        await job_manager.fail_job(job_id, str(e))
        raise


def process_dag_results(results: dict[str, Any]) -> dict[str, Any]:
    """
    Process DAG execution results into a format suitable for storage.

    Args:
        results: Raw DAG execution results

    Returns:
        Processed results dictionary
    """

    def convert_paths(obj: Any) -> Any:
        """Convert Path objects to strings recursively."""
        from pathlib import Path

        if isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: convert_paths(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_paths(i) for i in obj]
        return obj

    # Convert all results to JSON-serializable format
    processed: dict[str, Any] = {
        "node_results": {},
        "outputs": {},
        "metadata": {
            "completed_nodes": list(results.keys()),
            "has_errors": False,
        },
    }

    for node_id, node_result in results.items():
        # Convert any Path objects in the results to strings
        processed_result = convert_paths(node_result)
        processed["node_results"][node_id] = processed_result

        # If node produced output files, store their paths
        if isinstance(processed_result, dict):
            if "output_paths" in processed_result:
                processed["outputs"][node_id] = processed_result["output_paths"]
            elif "visualization" in processed_result:
                processed["outputs"][node_id] = processed_result["visualization"]

    return processed


async def execute_workflow(
    workflow_id: UUID,
    job_manager: JobManager,
    session: AsyncSession,
    start_node: str | None = None,
) -> UUID:
    """
    Execute a workflow as a job.

    Args:
        workflow_id: Workflow identifier
        job_manager: Job manager instance
        session: Database session
        start_node: Optional starting node

    Returns:
        Created job ID

    Raises:
        HTTPException: If workflow not found or execution fails
    """
    try:
        # Get workflow config
        workflow = await session.get(Workflow, workflow_id)
        if not workflow:
            logger.error(f"Workflow {workflow_id} not found")
            raise HTTPException(status_code=404, detail="Workflow not found")

        # Validate workflow config with GraphCap DAG
        try:
            # Log the workflow configuration for debugging
            logger.debug(f"Workflow config: {workflow.config}")

            # Ensure workflow.config has a 'nodes' key
            if "nodes" not in workflow.config:
                logger.error(f"Invalid workflow config format - missing 'nodes' key: {workflow.config}")
                raise ValueError("Workflow configuration must contain a 'nodes' list")

            dag = DAG.from_dict(workflow.config, node_classes=NODE_CLASS_MAPPINGS)
            dag.validate()
            logger.info(f"Workflow {workflow_id} DAG validated successfully")
        except Exception as e:
            logger.error(f"Workflow {workflow_id} validation failed: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid workflow configuration: {str(e)}")

        # Create pipeline config - pass the entire workflow config
        pipeline_config = PipelineConfig(
            config=workflow.config,  # Pass the entire config which contains the 'nodes' key
            start_node=start_node,
        )

        # Create and start job
        job_id = await job_manager.create_job(str(workflow_id), pipeline_config.model_dump())
        logger.info(
            "Workflow execution started",
            extra={
                "workflow_id": workflow_id,
                "job_id": job_id,
                "start_node": start_node,
                "config": workflow.config,  # Log the config for debugging
            },
        )

        return job_id

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(
            "Workflow execution failed",
            error=str(e),
            workflow_id=workflow_id,
            start_node=start_node,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute workflow: {str(e)}",
        )
