import asyncio
import json
import os
from pathlib import Path
from typing import List, Optional

import click
import uvicorn
from dotenv import load_dotenv
from graphcap.caption.batch_config import get_image_paths, load_batch_config

# from graphcap.caption.graph_caption import GraphCaptionProcessor
from graphcap.caption.nodes import PerspectiveNode
from graphcap.caption.perspectives.art_critic import ArtCriticProcessor
from graphcap.dataset.dataset_manager import DatasetConfig, DatasetManager
from graphcap.providers.provider_manager import ProviderManager
from loguru import logger

from .dag.dag import DAG
from .io import ImageSamplingNode

load_dotenv()


@click.group()
def cli():
    """graphcap CLI tool"""
    pass


@cli.command()
@click.option("--port", default=32100, help="Port to run the server on")
def dev(port):
    """Development server command."""
    uvicorn.run("graphcap.server:app", host="0.0.0.0", port=port, reload=True)


@cli.command()
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.option("--provider", "-p", default="openai", help="AI provider to use")
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output JSONL file path")
@click.option("--max-tokens", default=4096, help="Maximum tokens to generate")
@click.option("--temperature", default=0.8, help="Sampling temperature")
@click.option("--top-p", default=0.9, help="Nucleus sampling threshold")
@click.option(
    "--provider-config",
    "-c",
    default="provider.config.toml",
    type=click.Path(path_type=Path),
    help="Provider config file path",
)
@click.option(
    "--caption-type",
    "-t",
    default="graph",
    type=click.Choice(["graph", "art"]),
    help="Type of caption to generate",
)
def batch_caption(input_path, provider, output, max_tokens, temperature, top_p, provider_config, caption_type):
    """Process images from a directory or file and generate structured captions.

    INPUT_PATH: Directory containing images or a single image file
    """
    # Get list of image files
    image_paths = []
    if input_path.is_dir():
        # Supported image extensions
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        for ext in image_extensions:
            image_paths.extend(input_path.glob(f"**/*{ext}"))
    else:
        image_paths = [input_path]

    if not image_paths:
        logger.error("No image files found")
        return

    logger.info(f"Found {len(image_paths)} images to process")

    # Initialize provider
    provider_manager = ProviderManager(provider_config)
    provider_client = provider_manager.get_client(provider)

    if not provider_client:
        logger.error(f"Provider {provider} not found")
        return

    # Initialize caption processor based on type
    if caption_type == "graph":
        processor = GraphCaptionProcessor()
    else:  # art
        processor = ArtCriticProcessor()

    # Process images
    results = asyncio.run(
        processor.process_batch(
            provider=provider_client,
            image_paths=image_paths,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
    )

    # Write results
    if output:
        with output.open("w") as f:
            for result in results:
                f.write(json.dumps(result) + "\n")
        logger.info(f"Results written to {output}")
    else:
        # Print to stdout
        for result in results:
            print(json.dumps(result))


@cli.command()
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.option("--name", required=True, help="Name for the Hugging Face dataset")
@click.option("--description", required=True, help="Dataset description")
@click.option("--tags", multiple=True, help="Dataset tags")
@click.option("--push-to-hub/--local-only", default=False, help="Push to Hugging Face Hub")
@click.option("--private", is_flag=True, help="Private dataset")
@click.option("--use-hf-urls", is_flag=True, help="Use HuggingFace URLs for image paths instead of relative paths")
def export_dataset(
    input_path: Path,
    name: str,
    description: str,
    tags: List[str],
    push_to_hub: bool,
    private: bool = False,
    use_hf_urls: bool = False,
):
    """Export captions to a Hugging Face dataset format.

    INPUT_PATH: Path to JSONL file containing captions
    """

    async def _async_export():
        try:
            # Initialize dataset manager with the input path's parent directory
            dataset_manager = DatasetManager(input_path.parent)

            # Create dataset config
            config = DatasetConfig(
                name=name,
                description=description,
                tags=list(tags),
                include_images=True,  # Enable image uploads
                use_hf_urls=use_hf_urls,  # Use the new option
            )

            # Load captions from input file
            captions = []
            with input_path.open() as f:
                for line in f:
                    captions.append(json.loads(line))

            # Export to JSONL and create dataset
            if push_to_hub:
                # Check for HF token
                hf_token = os.getenv("HUGGING_FACE_HUB_TOKEN")
                if not hf_token:
                    logger.error("HUGGING_FACE_HUB_TOKEN environment variable not set")
                    return

                # Get repo ID for HF URLs if needed
                repo_id = f"{name}" if use_hf_urls else None

                # Create and push dataset using the input path directly
                result = await dataset_manager.create_hf_dataset(
                    input_path,  # Pass the input path directly
                    config,
                    push_to_hub=True,
                    token=hf_token,
                    private=private,
                    use_hf_urls=use_hf_urls,
                    repo_id=repo_id,
                )
                logger.info(f"Dataset pushed to Hugging Face Hub: {result}")
            else:
                logger.info(f"Dataset exported locally: {input_path}")

        except Exception as e:
            logger.error(f"Dataset export failed: {str(e)}")
            raise

    asyncio.run(_async_export())


@cli.command()
@click.option(
    "--provider-config",
    "-c",
    default="provider.config.toml",
    type=click.Path(path_type=Path),
    help="Provider config file path",
)
def list_providers(provider_config):
    """List all available AI providers configured in the system."""
    try:
        provider_manager = ProviderManager(provider_config)
        available_providers = provider_manager.get_available_providers()

        if not available_providers:
            logger.info("No providers configured")
            return

        logger.info("Available providers:")
        for provider in available_providers:
            logger.info(f"- {provider}")

    except Exception as e:
        logger.error(f"Failed to list providers: {str(e)}")
        raise


@cli.command()
@click.argument("config_file", type=click.Path(exists=True, path_type=Path))
def batch_config(config_file):
    """Process images using a TOML configuration file.

    CONFIG_FILE: Path to TOML configuration file
    """
    try:
        # Load and validate configuration
        config = load_batch_config(config_file)

        # Initialize provider
        provider_manager = ProviderManager(config.provider.config_file)
        provider_client = provider_manager.get_client(config.provider.name)

        if not provider_client:
            logger.error(f"Provider {config.provider.name} not found")
            return

        # Initialize caption processor based on type
        if config.caption.type == "graph":
            processor = GraphCaptionProcessor()
        else:  # art
            processor = ArtCriticProcessor()

        # Get image paths with sampling
        image_paths, sampling_info = get_image_paths(config.input)

        # Process images with output directory and logging
        _ = asyncio.run(
            processor.process_batch(
                provider=provider_client,
                image_paths=image_paths,
                max_tokens=config.caption.max_tokens,
                temperature=config.caption.temperature,
                top_p=config.caption.top_p,
                max_concurrent=config.provider.max_concurrent,
                repetition_penalty=config.caption.repetition_penalty,
                output_dir=config.output.directory,
                store_logs=config.output.store_logs,
                formats=config.output.formats,
                copy_images=config.output.copy_images,
            )
        )

    except Exception as e:
        logger.error(f"Error processing configuration: {e}")


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
                type_mappings = json.load(f)
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
    from graphcap.io.nodes import NODE_TYPES as IO_NODES

    # Combine all node registries
    registry = {}
    registry.update(CAPTION_NODES)
    registry.update(IO_NODES)
    registry.update(DAG_NODES)  # Add DAG nodes

    return registry


if __name__ == "__main__":
    cli()
