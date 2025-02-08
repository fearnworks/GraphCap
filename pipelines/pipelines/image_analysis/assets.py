# SPDX-License-Identifier: Apache-2.0
"""Image analysis assets."""

import os
import json
import dagster as dg
from typing import List, Dict

@dg.asset(name="raw_images")
def raw_images_asset(context: dg.AssetExecutionContext) -> List[str]:
    """Load raw images from directory."""
    image_dir = "/workspace/datasets/os_img"
    context.log.info(f"Loading images from: {image_dir}")
    return [f"{image_dir}/image_{i}.jpg" for i in range(5)]

@dg.asset(name="art_analysis_results", deps=[raw_images_asset])
def art_analysis_results_asset(
    context: dg.AssetExecutionContext, 
    raw_images: List[str]
) -> Dict[str, str]:
    """Perform art analysis on images."""
    context.log.info(f"Performing art analysis on {len(raw_images)} images")
    results = {}
    for image_path in raw_images:
        results[image_path] = f"Art analysis result for {image_path}"
    return results

@dg.asset(name="final_dataset", deps=[art_analysis_results_asset])
def final_dataset_asset(
    context: dg.AssetExecutionContext, 
    art_analysis_results: Dict[str, str]
) -> str:
    """Export analysis results to dataset."""
    context.log.info("Exporting dataset...")
    dataset_path = "/workspace/.local/output/dags/smoke/dataset.json"
    with open(dataset_path, 'w') as f:
        json.dump(art_analysis_results, f, indent=4)
    return dataset_path 