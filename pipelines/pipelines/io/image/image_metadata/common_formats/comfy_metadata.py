# SPDX-License-Identifier: Apache-2.0
"""
comfy_metadata module

Provides functionality to extract ComfyUI metadata from image descriptions.
This asset extracts specific ComfyUI parameters (e.g. a comfy prompt) and
associates them with the unique identifier of the core image.
"""

from typing import Any, Dict

import pandas as pd
from dagster import AssetExecutionContext, asset

from ...types import DatasetIOConfig  # Adjust relative import as needed


def extract_comfyui_parameters(description: str) -> Dict[str, Any]:
    """
    Extract ComfyUI parameters from the description text.
    Searches for a 'ComfyUI:' marker and extracts the following text.

    Args:
        description (str): The image description text.

    Returns:
        Dict[str, Any]: Extracted ComfyUI-specific metadata.
    """
    print("Stubbed ComfyUI metadata extraction")
    return {}


@asset(
    group_name="image_metadata",
    compute_kind="python",
    description="Extracts ComfyUI metadata from image descriptions and stores it in a Parquet and JSON file.",
)
def comfy_metadata(
    context: AssetExecutionContext,
    image_list_exif_data: str,
    image_dataset_config: DatasetIOConfig,
) -> None:
    """
    Extracts ComfyUI metadata from image descriptions.

    Args:
        context: Dagster execution context for logging.
        image_list_exif_data: Path to the Parquet file containing Exif metadata.
        image_dataset_config: Dataset configuration including output directory.
    """
    context.log.info("Extracting ComfyUI metadata from image descriptions")

    df_exif = pd.read_parquet(image_list_exif_data)
    comfy_data = []

    context.log.info("ComfyUI metadata extraction stub complete")
