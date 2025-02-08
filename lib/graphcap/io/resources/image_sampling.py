# graphcap/io/resources/image_sampling_resource.py

import random
from pathlib import Path
from typing import Any, Dict, List, Literal

from dagster import ConfigurableResource, InitResourceContext
from pydantic import BaseModel, Field


class ImageSamplingConfig(BaseModel):
    """Configuration schema for ImageSamplingResource."""

    path: str = Field(..., description="Path to image directory or file")
    sample_size: int = Field(0, default=0, description="Number of images to sample (0 for all)")
    sample_method: Literal["random", "incremental", "latest"] = Field(
        "random", default="random", description="Sampling method"
    )


class ImageSamplingResource(ConfigurableResource[ImageSamplingConfig]):
    """
    Resource for loading and sampling images from a directory.
    """

    def sample_images(self, path: Path, sample_size: int, sample_method: str) -> Dict[str, Any]:
        """
        Samples images from the specified path based on resource configuration.

        Args:
            path (Path): Path to image directory or file (already validated Path object).
            sample_size (int): Number of images to sample.
            sample_method (str): Sampling method.

        Returns:
            Dict[str, Any]: Dictionary containing image_paths and sampling_info.
        """
        image_paths: List[Path] = []

        # Get image paths (logic from ImageSamplingNode.sample)
        if path.is_dir():
            image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
            for ext in image_extensions:
                image_paths.extend(path.glob(f"**/*{ext}"))
        else:
            image_paths = [path]

        if not image_paths:
            raise ValueError(f"No image files found in {path}")  # or handle differently?

        original_count = len(image_paths)

        # Apply sampling (logic from ImageSamplingNode.sample)
        if sample_size > 0 and sample_size < len(image_paths):
            if sample_method == "random":
                image_paths = random.sample(image_paths, sample_size)
            elif sample_method == "incremental":
                image_paths = image_paths[:sample_size]
            elif sample_method == "latest":
                sorted_paths = sorted(image_paths, key=lambda p: p.stat().st_mtime, reverse=True)[:sample_size]
                image_paths = sorted_paths

        sampling_info = {
            "original_count": original_count,
            "sample_size": len(image_paths),
            "sample_method": sample_method if sample_size > 0 else "all",
        }
        return {
            "image_paths": [str(p) for p in image_paths],
            "sampling_info": sampling_info,
        }  # Return paths as strings for now

    def _validate_path(self, path_str: str) -> Path:  # Helper method - keep validation logic
        """Validates and converts path string to Path object."""
        input_path = Path(path_str)  # Take string input from config
        if not input_path.exists():
            raise ValueError(f"Path does not exist: {path_str}")
        return input_path

    def setup_for_execution(
        self, context: InitResourceContext
    ):  # Setup lifecycle hook (optional for this resource, but good practice)
        """Resource setup - currently empty, but could be used for connection setup in future."""
        pass

    def teardown_after_execution(self, context: InitResourceContext):  # Teardown lifecycle hook (optional)
        """Resource teardown - currently empty."""
        pass

    def __init__(self, init_context: InitResourceContext):  # Constructor - takes InitResourceContext
        super().__init__(init_context)
        self._config = (
            init_context.resource_config
        )  # Store config if needed, though direct access via self.config is also possible


image_sampling_resource = ImageSamplingResource.as_resource()  # Create Dagster ResourceDefinition
