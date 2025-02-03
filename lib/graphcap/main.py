import asyncio
import json
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv
from loguru import logger

# from graphcap.caption.graph_caption import GraphCaptionProcessor
from graphcap.caption.nodes import PerspectiveNode

from .dag.dag import DAG
from .io import ImageSamplingNode

load_dotenv()


@click.group()
def cli():
    """graphcap CLI tool"""
    pass


# Add this dictionary to map node types to their classes
NODE_CLASS_MAPPINGS = {
    "ImageSamplingNode": ImageSamplingNode,
    "PerspectiveNode": PerspectiveNode,
}


@cli.command("dag-validate")
@click.argument("dag_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--node-types", type=click.Path(exists=True, path_type=Path), help="JSON file mapping node types to classes"
)
def dag_validate(dag_file: Path, node_types: Optional[Path] = None):
    """
    Validate a DAG configuration file.

    The configuration file should be in JSON format with nodes and their dependencies.
    """
    try:
        # Use built-in node mappings
        node_classes = NODE_CLASS_MAPPINGS.copy()

        # Load additional node type mappings if provided
        if node_types:
            with node_types.open() as f:
                _ = json.load(f)
                # Add custom mappings to node_classes
                pass

        DAG.validate_config(str(dag_file), node_classes)

    except Exception as e:
        logger.error(f"DAG validation failed: {e}")


@cli.command("dag-run")
@click.argument("dag_file", type=click.Path(exists=True, path_type=Path))
@click.option("--start-node", help="Optional node ID to start execution from")
def dag_run(dag_file: Path, start_node: Optional[str] = None):
    """Execute a DAG configuration."""
    try:
        # Get node registry
        node_classes = get_node_registry()

        # Create and validate DAG
        dag = DAG.validate_config(str(dag_file), node_classes)

        # Execute DAG
        results = asyncio.run(dag.execute(start_node))

        logger.info("DAG execution completed successfully")
        for node_id, result in results.items():
            logger.info(f"Node {node_id} result: {result}")

    except Exception as e:
        logger.error(f"DAG execution failed: {e}")


def get_node_registry():
    """Get complete node registry."""
    from graphcap.caption.nodes import NODE_TYPES as CAPTION_NODES
    from graphcap.dag.nodes import NODE_TYPES as DAG_NODES
    from graphcap.dataset.nodes import NODE_TYPES as DATASET_NODES
    from graphcap.io.nodes import NODE_TYPES as IO_NODES

    # Combine all node registries
    registry = {}
    registry.update(CAPTION_NODES)
    registry.update(IO_NODES)
    registry.update(DAG_NODES)
    registry.update(DATASET_NODES)

    return registry


if __name__ == "__main__":
    cli()
