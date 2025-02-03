"""
# SPDX-License-Identifier: Apache-2.0
graphcap.io.nodes.image_sampling

Provides node implementation for loading and sampling images from a directory.

Key features:
- Directory scanning
- Multiple sampling methods
- Image format validation
- Path filtering
"""

import random
from pathlib import Path
from typing import Any, Dict, List

from ...dag.node import BaseNode


class ImageSamplingNode(BaseNode):
    """
    Node for loading and sampling images from a directory.

    Supports multiple sampling methods and image format validation.
    """

    @classmethod
    def schema(cls) -> Dict[str, Dict[str, Any]]:
        """Define node schema."""
        return {
            "required": {
                "path": {
                    "type": "STRING",
                    "default": "./images",
                    "description": "Path to image directory or file",
                },
                "sample_size": {
                    "type": "INT",
                    "default": 0,
                    "min": 0,
                    "max": 1000,
                    "description": "Number of images to sample (0 for all)",
                },
                "sample_method": {
                    "type": "ENUM",
                    "values": ["random", "incremental", "latest"],
                    "default": "random",
                    "description": "Method to use for sampling",
                },
            }
        }

    @property
    def outputs(self) -> Dict[str, str]:
        """Define node outputs."""
        return {
            "image_paths": "LIST[PATH]",
            "sampling_info": "DICT",
        }

    @property
    def category(self) -> str:
        """Define node category."""
        return "IO"

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute image sampling."""
        self.validate_inputs(**kwargs)
        result = await self.sample(**kwargs)
        return result

    def _validate_path(self, path: str) -> Path:
        """
        Validate and convert path string to Path object.

        Args:
            path: Path string to validate

        Returns:
            Path object if valid

        Raises:
            ValueError: If path doesn't exist
        """
        input_path = Path(path)
        if not input_path.exists():
            raise ValueError(f"Path does not exist: {path}")
        return input_path

    async def sample(self, path: str, sample_size: int = 0, sample_method: str = "random") -> Dict[str, Any]:
        """
        Sample images from the specified path.

        Args:
            path: Directory or file path
            sample_size: Number of images to sample (0 means use all)
            sample_method: Sampling method to use

        Returns:
            Dict containing image_paths and sampling_info

        Raises:
            ValueError: If path doesn't exist or no images found
        """
        # Validate path first
        input_path = self._validate_path(path)
        image_paths: List[Path] = []

        # Get image paths
        if input_path.is_dir():
            image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
            for ext in image_extensions:
                image_paths.extend(input_path.glob(f"**/*{ext}"))
        else:
            image_paths = [input_path]

        if not image_paths:
            raise ValueError(f"No image files found in {path}")

        original_count = len(image_paths)

        # Apply sampling if requested
        if sample_size > 0 and sample_size < len(image_paths):
            if sample_method == "random":
                image_paths = random.sample(image_paths, sample_size)
            elif sample_method == "incremental":
                image_paths = image_paths[:sample_size]
            elif sample_method == "latest":
                # Sort by modification time, newest first
                image_paths = sorted(image_paths, key=lambda p: p.stat().st_mtime, reverse=True)[:sample_size]

        # Prepare sampling info
        sampling_info = {
            "original_count": original_count,
            "sample_size": len(image_paths),
            "sample_method": sample_method if sample_size > 0 else "all",
        }

        return {"image_paths": image_paths, "sampling_info": sampling_info}
