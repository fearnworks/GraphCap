# SPDX-License-Identifier: Apache-2.0
"""
common_formats module

Provides functionality to extract Midjourney style metadata from image descriptions.
"""

import re
from pathlib import Path
from typing import List, Optional, TypedDict

import pandas as pd
from dagster import AssetExecutionContext, asset

from ...types import DatasetIOConfig


class MidjourneyMetadata(TypedDict, total=False):
    """Metadata extracted from Midjourney prompts."""

    aspect_ratio: Optional[str]
    chaos: Optional[int]
    character_reference: Optional[bool]
    fast: Optional[bool]
    image_weight: Optional[float]
    no: Optional[str]
    quality: Optional[float]
    random_style: Optional[str]
    relax: Optional[bool]
    repeat: Optional[int]
    seed: Optional[int]
    stop: Optional[int]
    style: Optional[str]
    stylize: Optional[int]
    tile: Optional[bool]
    turbo: Optional[bool]
    video: Optional[bool]
    weird: Optional[int]
    model_version: Optional[str]
    image_refs: Optional[List[str]]
    srefs: Optional[List[str]]
    crefs: Optional[List[str]]
    main_description: Optional[str]
    command: Optional[str]


def extract_midjourney_parameters(description: str) -> MidjourneyMetadata:
    """
    Extract Midjourney parameters from the description field.

    Args:
        description (str): The description text containing Midjourney parameters.

    Returns:
        MidjourneyMetadata: Extracted parameters.
    """
    params: MidjourneyMetadata = {}

    # Store the original command
    params["command"] = description

    # Extract initial image references
    initial_refs = re.findall(r"https:\/\/s\.mj\.run\/\w+", description)
    if initial_refs:
        params["image_refs"] = initial_refs
        # Remove initial image refs from description
        description = re.sub(r"https:\/\/s\.mj\.run\/\w+\s*", "", description, count=len(initial_refs))

    # Extract --sref image references
    srefs = re.findall(r"--sref\s+(https:\/\/s\.mj\.run\/\w+)", description)
    if srefs:
        params["srefs"] = srefs
        description = re.sub(r"--sref\s+https:\/\/s\.mj\.run\/\w+", "", description)

    # Extract --cref image references
    crefs = re.findall(r"--cref\s+(https:\/\/s\.mj\.run\/\w+)", description)
    if crefs:
        params["crefs"] = crefs
        description = re.sub(r"--cref\s+https:\/\/s\.mj\.run\/\w+", "", description)

    # Extract main description (text before parameters)
    main_desc_match = re.match(r"^(.*?)\s*(--\w+|Job ID:)", description, re.DOTALL)
    if main_desc_match:
        params["main_description"] = main_desc_match.group(1).strip()
    else:
        params["main_description"] = description.strip()

    # Define regex patterns for each parameter
    patterns = {
        "aspect_ratio": r"--(?:aspect|ar) (\d+:\d+)",
        "chaos": r"--chaos (\d{1,3})",
        "fast": r"--fast\b",
        "image_weight": r"--iw (\d(?:\.\d)?)",
        "no": r"--no ([\w\s]+)",
        "quality": r"--(?:quality|q) (\.25|\.5|1)",
        "random_style": r"--style random(?:-\d+)?",
        "relax": r"--relax\b",
        "repeat": r"--(?:repeat|r) (\d{1,2})",
        "seed": r"--(?:seed|sameseed) (\d{1,10})",
        "stop": r"--stop (\d{2,3})",
        "style": r"--style (\w+)",
        "stylize": r"--(?:stylize|s) (\d{1,4})",
        "tile": r"--tile\b",
        "turbo": r"--turbo\b",
        "video": r"--video\b",
        "weird": r"--(?:weird|w) (\d{1,4})",
        "model_version": r"--(?:version|v) ([\d\.]+)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            if key in ["fast", "relax", "tile", "turbo", "video"]:
                params[key] = True
            elif key == "no":
                params[key] = match.group(1)
            elif key in ["chaos", "repeat", "seed", "stop", "stylize", "weird"]:
                params[key] = int(match.group(1))
            elif key == "image_weight":
                params[key] = float(match.group(1))
            else:
                params[key] = match.group(1)

    return params


@asset(
    group_name="image_metadata",
    compute_kind="python",
    description="Extracts Midjourney style metadata from image descriptions and stores it in a Parquet and JSON file.",
)
def midjourney_metadata(
    context: AssetExecutionContext,
    image_list_exif_data: str,
    image_dataset_config: DatasetIOConfig,
) -> None:
    """
    Extract Midjourney metadata from image descriptions.

    Args:
        image_list_exif_data: Path to the Parquet file containing Exif metadata
        context: Dagster context for logging
        image_dataset_config: Dataset configuration
    """

    context.log.info("Extracting Midjourney metadata from image descriptions")

    midjourney_data = []
    exif_df = pd.read_parquet(image_list_exif_data)
    for _, row in exif_df.iterrows():
        description = row.get("Description", "")

        extracted_params = extract_midjourney_parameters(description)
        midjourney_data.append(extracted_params)

    # Create a DataFrame from extracted parameters
    midjourney_df = pd.DataFrame(midjourney_data)

    # Merge EXIF data with Midjourney parameters
    combined_df = pd.concat([exif_df.reset_index(drop=True), midjourney_df.reset_index(drop=True)], axis=1)

    # Define output paths
    output_parquet = Path(image_dataset_config.output_dir) / "metadata/midjourney_metadata_combined.parquet"
    output_json = Path(image_dataset_config.output_dir) / "metadata/midjourney_metadata_combined.json"

    # Save the combined DataFrame
    combined_df.to_parquet(output_parquet)
    combined_df.to_json(output_json, orient="records", lines=True)

    context.log.info(f"Combined Midjourney metadata saved to: {output_parquet}")
    context.log.info(f"Combined Midjourney metadata also saved to: {output_json}")
