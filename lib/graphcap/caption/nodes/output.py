"""
# SPDX-License-Identifier: Apache-2.0
graphcap.caption.nodes.output

Provides node implementation for saving perspective outputs.

Key features:
- Standardized output handling
- Configurable output directory
- Image copying support
- Log storage
"""

from pathlib import Path
from typing import Any

from loguru import logger

from ...dag.node import BaseNode


class PerspectiveOutputNode(BaseNode):
    """
    Node for saving perspective outputs.

    Handles saving perspective results to disk in a standardized format,
    with optional image copying and log storage.

    Attributes:
        category (str): Node category identifier
    """

    @classmethod
    def schema(cls) -> dict[str, Any]:
        """
        Define node schema.

        Returns:
            Schema definition for node configuration
        """
        return {
            "type": "object",
            "required": ["output", "perspective_type"],
            "properties": {
                "perspective_type": {
                    "type": "STRING",
                    "description": "Type of perspective being processed",
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
    def category(self) -> str:
        """Define node category."""
        return "Output"

    @property
    def outputs(self) -> dict[str, str]:
        """
        Define node outputs.

        Returns:
            Dictionary mapping output names to their types
        """
        return {
            "output_paths": "DICT",
        }

    def validate_inputs(self, **kwargs) -> None:
        """Validate node inputs."""
        required = {"perspective_results", "output", "perspective_type"}
        missing = required - set(kwargs.keys())
        if missing:
            raise ValueError(f"Missing required inputs: {missing}")

        if not isinstance(kwargs["output"], dict):
            raise ValueError("output must be a dictionary")

    async def execute(self, **kwargs) -> dict[str, Any]:
        """
        Execute output processing.

        Args:
            **kwargs: Node parameters including:
                perspective_results: List of results from perspective processing
                output: Output configuration
                perspective_type: Type of perspective

        Returns:
            Dictionary containing output paths and status
        """
        self.validate_inputs(**kwargs)

        perspective_results = kwargs["perspective_results"]
        output_config = kwargs["output"]
        perspective_type = kwargs["perspective_type"]

        # Create output directory
        output_dir = Path(output_config["directory"])
        output_dir.mkdir(parents=True, exist_ok=True)

        output_paths = {"analyses": [], "images": [], "logs": []}

        # Process each result
        for result_data in perspective_results:
            # Write structured JSON output
            analysis_file = output_dir / f"{perspective_type}_response.json"
            with analysis_file.open("a") as f:
                f.write(f"{result_data}\n")
            output_paths["analyses"].append(str(analysis_file))

            # Copy image if requested
            if output_config.get("copy_images", False):
                image_path = Path(result_data["filename"])
                if image_path.exists():
                    dest_path = output_dir / "images" / image_path.name
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    dest_path.write_bytes(image_path.read_bytes())
                    logger.info(f"Copied image to {dest_path}")
                    output_paths["images"].append(str(dest_path))

            # Store logs if requested
            if output_config.get("store_logs", True):
                log_file = output_dir / f"{perspective_type}_processing.log"
                with log_file.open("a") as f:
                    f.write(f"Processed {result_data['filename']}\n")
                    f.write(f"Model: {result_data.get('model', 'unknown')}\n")
                    f.write(f"Provider: {result_data.get('provider', 'unknown')}\n")
                    f.write("---\n")
                output_paths["logs"].append(str(log_file))

        return {"output_paths": output_paths}
