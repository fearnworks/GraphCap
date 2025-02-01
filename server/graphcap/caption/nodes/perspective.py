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

from ...dag.node import BaseNode
from ...providers.provider_manager import ProviderManager
from ..perspectives import ArtCriticProcessor, GraphCaptionProcessor
from ..perspectives.base import BasePerspective


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
        """
        Execute perspective processing on images.

        Args:
            image_paths: List of paths to images
            perspective_type: Type of perspective to use
            max_tokens: Maximum tokens for model response
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            max_concurrent: Maximum concurrent requests
            output_dir: Optional output directory
            formats: Optional list of output formats

        Returns:
            Dict containing captions and perspective info
        """
        # Validate inputs
        self.validate_inputs(**kwargs)

        # Get parameters
        image_paths: List[Path] = [Path(p) for p in kwargs["image_paths"]]
        perspective_type = kwargs["perspective_type"]
        provider_name = kwargs.get("provider_name", "openai")

        # Get model parameters
        model_params = kwargs.get("model_params", {})
        max_tokens = model_params.get("max_tokens", 4096)
        temperature = model_params.get("temperature", 0.8)
        top_p = model_params.get("top_p", 0.9)
        max_concurrent = model_params.get("max_concurrent", 5)

        # Get output configuration
        output_config = kwargs.get("output", {})
        output_dir = Path(output_config.get("directory", "./outputs"))
        formats = output_config.get("formats", ["html"])
        store_logs = output_config.get("store_logs", True)
        copy_images = output_config.get("copy_images", False)

        if not image_paths:
            raise ValueError("No image paths provided")

        # Create perspective processor
        if perspective_type not in self.PERSPECTIVE_TYPES:
            raise ValueError(f"Unknown perspective type: {perspective_type}")

        processor_class = self.PERSPECTIVE_TYPES[perspective_type]
        processor: BasePerspective = processor_class()

        # Initialize provider if not already done
        if not self._provider:
            provider_manager = ProviderManager()
            self._provider = provider_manager.get_client(provider_name)

        # Process images
        try:
            results = await processor.process_batch(
                provider=self._provider,
                image_paths=image_paths,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                max_concurrent=max_concurrent,
                output_dir=output_dir,
                store_logs=store_logs,
                formats=formats,
                copy_images=copy_images,
            )

            # Prepare return data
            perspective_info = {
                "type": perspective_type,
                "total_images": len(image_paths),
                "successful": len([r for r in results if "error" not in r["parsed"]]),
                "output_dir": str(output_dir),
                "formats": formats,
            }

            return {
                "captions": results,
                "perspective_info": perspective_info,
            }

        except Exception as e:
            logger.error(f"Perspective processing failed: {str(e)}")
            raise
