"""
# SPDX-License-Identifier: Apache-2.0
graphcap.caption.nodes.perspective

Provides node implementation for running caption perspectives on images.

Key features:
- Multiple perspective support
- Batch processing
- Result aggregation
- Progress tracking
- Configurable outputs
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ...dag.node import BaseNode
from ...providers.provider_manager import ProviderManager
from ..perspectives import ArtCriticProcessor, GraphCaptionProcessor


@retry(
    retry=retry_if_exception_type((KeyError, ConnectionError)),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
)
async def process_with_retries(
    processor: Any,
    provider: Any,
    image_paths: list[str],
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """
    Process images with retries.

    Args:
        processor: The perspective processor to use
        provider: The provider client
        image_paths: List of image paths to process
        **kwargs: Additional arguments for processing

    Returns:
        List of processing results

    Raises:
        Exception: If processing fails after all retries
    """
    return await processor.process_batch(
        provider=provider,
        image_paths=image_paths,
        **kwargs,
    )


class PerspectiveNode(BaseNode):
    """
    Node for running caption perspectives on images.

    Processes images through different caption perspectives like graph analysis
    or art critic analysis, producing structured descriptions and analysis.
    """

    PERSPECTIVE_TYPES = {
        "graph": GraphCaptionProcessor,
        "art": ArtCriticProcessor,
    }

    def __init__(self, id: str, dependencies: Optional[List[str]] = None):
        super().__init__(id, dependencies)
        self._provider = None

    @classmethod
    def schema(cls) -> Dict[str, Dict[str, Any]]:
        """Define node schema."""
        return {
            "required": {
                "image_paths": {
                    "type": "LIST[PATH]",
                    "description": "List of paths to images to process",
                },
                "perspective_type": {
                    "type": "ENUM",
                    "values": list(cls.PERSPECTIVE_TYPES.keys()),
                    "default": "graph",
                    "description": "Type of perspective to use",
                },
                "provider_name": {
                    "type": "STRING",
                    "default": "openai",
                    "description": "Name of the provider to use",
                },
            },
            "optional": {
                "model_params": {
                    "type": "DICT",
                    "description": "Model parameters",
                    "properties": {
                        "max_tokens": {
                            "type": "INT",
                            "default": 4096,
                            "description": "Maximum tokens for model response",
                        },
                        "temperature": {
                            "type": "FLOAT",
                            "default": 0.8,
                            "description": "Sampling temperature",
                        },
                        "top_p": {
                            "type": "FLOAT",
                            "default": 0.9,
                            "description": "Nucleus sampling parameter",
                        },
                        "max_concurrent": {
                            "type": "INT",
                            "default": 5,
                            "description": "Maximum concurrent requests",
                        },
                    },
                },
                "output": {
                    "type": "DICT",
                    "description": "Output configuration",
                    "properties": {
                        "directory": {
                            "type": "PATH",
                            "description": "Base directory for outputs",
                            "default": "./outputs",
                        },
                        "store_logs": {
                            "type": "BOOL",
                            "description": "Whether to store processing logs",
                            "default": True,
                        },
                        "copy_images": {
                            "type": "BOOL",
                            "description": "Whether to copy images to output directory",
                            "default": False,
                        },
                    },
                },
            },
        }

    @property
    def outputs(self) -> Dict[str, str]:
        """Define node outputs."""
        return {
            "perspective_results": "LIST[DICT]",
        }

    @property
    def category(self) -> str:
        """Define node category."""
        return "Caption"

    def validate_inputs(self, **kwargs) -> None:
        """Validate node inputs."""
        required = {"image_paths", "perspective_type", "provider_name", "model_params", "output"}
        missing = required - set(kwargs.keys())
        if missing:
            raise ValueError(f"Missing required inputs: {missing}")

        if kwargs["perspective_type"] not in self.PERSPECTIVE_TYPES:
            raise ValueError(f"Invalid perspective type: {kwargs['perspective_type']}")

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute perspective processing."""
        self.validate_inputs(**kwargs)

        # Get image paths from input
        image_paths = kwargs["image_paths"]
        perspective_type = kwargs["perspective_type"]

        # Initialize processor
        processor_class = self.PERSPECTIVE_TYPES[perspective_type]
        processor = processor_class()

        # Initialize provider
        provider_manager = ProviderManager()
        provider = provider_manager.get_client(kwargs["provider_name"])

        try:
            # Process images with retries
            results = await process_with_retries(
                processor=processor,
                provider=provider,
                image_paths=image_paths,
                max_tokens=kwargs["model_params"]["max_tokens"],
                temperature=kwargs["model_params"]["temperature"],
                top_p=kwargs["model_params"]["top_p"],
                max_concurrent=kwargs["model_params"]["max_concurrent"],
            )

            # Write outputs for all results
            output_dir = Path(kwargs["output"]["directory"])
            for result in results:
                processor.write_outputs(output_dir, result)
                logger.debug(f"Wrote output for {result['filename']}")

            return {"perspective_results": results}

        except Exception as e:
            logger.error(f"Failed to process images with {perspective_type} perspective: {str(e)}")
            raise
