"""
# SPDX-License-Identifier: Apache-2.0
Workflow Service

Provides business logic for workflow management and execution.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import HTTPException
from graphcap.dag import DAG
from graphcap.node_index import NODE_CLASS_MAPPINGS
from loguru import logger
from server.features.job.manager import JobManager
from server.features.job.schemas import PipelineConfig
from server.features.workflows.schemas import CombinedPerspectiveResult, PerspectiveResult
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
    """Process DAG execution results into a format suitable for storage."""

    def get_perspective_type(node_id: str) -> str | None:
        """Extract perspective type from node ID."""
        if "art" in node_id.lower():
            return "art"
        elif "graph" in node_id.lower():
            return "graph"
        return None

    import pprint

    def is_valid_result(result: dict[str, Any]) -> bool:
        """Check if result is valid and not an error."""
        logger.debug("Validating perspective result")
        logger.debug(f"Result: {pprint.pformat(result)}")
        # Check each validation condition and log the result
        is_dict = isinstance(result, dict)

        logger.debug(f"Is dictionary: {is_dict}")
        if not is_dict:
            logger.warning("Result is not a dictionary")
            return False

        has_filename = "filename" in result
        logger.debug(f"Has filename: {has_filename}")
        if not has_filename:
            logger.warning("Result missing filename")
            return False

        has_parsed = "parsed" in result
        logger.debug(f"Has parsed data: {has_parsed}")
        if not has_parsed:
            logger.warning("Result missing parsed data")
            return False

        no_error = not result.get("error")
        logger.debug(f"No error present: {no_error}")
        if not no_error:
            logger.warning(f"Result contains error: {result.get('error')}")
            return False

        valid_analysis = result.get("formal_analysis") != "No formal analysis available"
        logger.debug(f"Has valid analysis: {valid_analysis}")
        if not valid_analysis:
            logger.warning("Result has invalid or missing formal analysis")
            return False

        # Log the full validation details
        logger.debug(
            "Validation details",
            extra={
                "result_keys": list(result.keys()),
                "has_filename": has_filename,
                "has_parsed": has_parsed,
                "no_error": no_error,
                "valid_analysis": valid_analysis,
                "result_content": result,
            },
        )

        if not (is_dict and has_filename and has_parsed and no_error and valid_analysis):
            logger.warning("Result validation failed")
            return False

        return True

    # Log incoming results
    logger.debug(
        "Processing DAG results",
        extra={
            "node_ids": list(results.keys()),
            "result_types": {k: type(v).__name__ for k, v in results.items()},
            "result_keys": {k: list(v.keys()) if isinstance(v, dict) else None for k, v in results.items()},
        },
    )

    perspective_results: dict[str, dict[str, Any]] = {}

    for node_id, node_result in results.items():
        if not isinstance(node_result, dict):
            logger.warning(
                f"Skipping non-dict result for node {node_id}", extra={"result_type": type(node_result).__name__}
            )
            continue

        perspective_type = get_perspective_type(node_id)
        if not perspective_type:
            logger.debug(f"Node {node_id} is not a perspective node")
            continue

        if is_valid_result(node_result):
            logger.info(
                f"Valid {perspective_type} result found",
                extra={
                    "node_id": node_id,
                    "filename": node_result["filename"],
                    "result_keys": list(node_result.keys()),
                },
            )
            perspective_results[perspective_type] = PerspectiveResult(
                filename=node_result["filename"],
                perspective_type=perspective_type,
                provider=node_result["provider"],
                model=node_result["model"],
                version=node_result["version"],
                parsed=node_result["parsed"],
                formal_analysis=node_result.get("formal_analysis"),
            ).model_dump()

    # Log perspective results
    logger.info(
        "Processed perspective results",
        extra={"perspective_count": len(perspective_results), "perspective_types": list(perspective_results.keys())},
    )

    # Create final combined result
    if perspective_results:
        first_result = next(iter(perspective_results.values()))
        combined = CombinedPerspectiveResult(
            filename=first_result["filename"], perspectives=perspective_results
        ).model_dump()

        result = {
            "result": combined,
            "metadata": {
                "perspectives": list(perspective_results.keys()),
                "has_errors": False,
                "timestamp": datetime.utcnow().isoformat(),
            },
        }
        logger.info(
            "Created combined result",
            extra={
                "filename": combined["filename"],
                "perspective_count": len(combined["perspectives"]),
                "has_errors": False,
            },
        )
        return result

    # Return error state if no valid perspectives
    logger.warning("No valid perspective results found")
    return {
        "error": "No valid perspective results generated",
        "metadata": {"perspectives": [], "has_errors": True, "timestamp": datetime.utcnow().isoformat()},
    }


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

        # Validate workflow config with graphcap DAG
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
