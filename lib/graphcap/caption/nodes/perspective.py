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

from typing import Any, Dict, List, Optional

from loguru import logger

from ...dag.node import BaseNode
from ...providers.provider_manager import ProviderManager
from ..perspectives import ArtCriticProcessor, GraphCaptionProcessor


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
                        "formats": {
                            "type": "LIST[STRING]",
                            "description": "Output formats to generate",
                            "default": ["dense"],
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
            "captions": "LIST[CAPTION]",
            "perspective_info": "DICT",
        }

    @property
    def category(self) -> str:
        """Define node category."""
        return "Caption"

    def validate_inputs(self, **kwargs) -> bool:
        """
        Validate node inputs.

        Args:
            **kwargs: Node input parameters

        Returns:
            True if inputs are valid

        Raises:
            ValueError: If required parameters are missing or invalid
        """
        # Check required parameters
        if "image_paths" not in kwargs:
            raise ValueError("Missing required parameter: image_paths")

        if "perspective_type" not in kwargs:
            raise ValueError("Missing required parameter: perspective_type")

        # Validate perspective type
        if kwargs["perspective_type"] not in self.PERSPECTIVE_TYPES:
            raise ValueError(
                f"Invalid value for perspective_type. Must be one of: {list(self.PERSPECTIVE_TYPES.keys())}"
            )

        # Validate model parameters
        model_params = kwargs.get("model_params", {})
        if not isinstance(model_params, dict):
            raise ValueError("model_params must be a dictionary")

        # Validate output configuration
        output_config = kwargs.get("output", {})
        if not isinstance(output_config, dict):
            raise ValueError("output must be a dictionary")

        return True

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

        # Process images
        results = await processor.process_batch(
            provider=provider,
            image_paths=image_paths,
            max_tokens=kwargs["model_params"]["max_tokens"],
            temperature=kwargs["model_params"]["temperature"],
            top_p=kwargs["model_params"]["top_p"],
            max_concurrent=kwargs["model_params"]["max_concurrent"],
        )

        # Format results for output node - handle first image's results
        first_result = results[0]  # Get first image result
        logger.debug(f"Raw processor result: {first_result}")

        # Extract content from parsed results
        parsed = first_result.get("parsed", {})
        logger.debug(f"Parsed content: {parsed}")

        perspective_results = {
            "formal": {
                "filename": "formal_analysis.txt",
                "content": parsed.get("formal_analysis", "No formal analysis available"),
            },
            "html": {
                "filename": "art_report.html",
                "content": first_result.get("html_report", "No HTML report available"),
            },
            "logs": first_result.get("logs", ""),
            "image_path": str(image_paths[0]),
        }

        logger.info(f"Formatted perspective results for output node: {list(perspective_results.keys())}")
        return {"perspective_results": perspective_results}
