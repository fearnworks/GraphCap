# SPDX-License-Identifier: Apache-2.0
"""Asset exports for the pipeline package.

This module provides a central point for importing and re-exporting all assets
used in the pipeline system. This simplifies imports in other modules and provides
a clear overview of available assets.

Key features:
- Centralized asset imports
- Organized by feature area
- Type-safe exports
"""

# Feature imports
from .image_analysis import (
    raw_images_asset,
    art_analysis_results_asset,
    final_dataset_asset
)
from .caption_generation.perspectives import (
    image_selection_asset,
    provider_selection_asset,
    caption_generation_asset
)
from .huggingface.dataset_export import (
    dataset_metadata_asset,
    dataset_verification_asset,
    huggingface_upload_asset
)
from .huggingface.dataset_import import (
    dataset_download_asset,
    dataset_validation_asset
)

# Re-export all assets
__all__ = [
    # Image analysis
    "raw_images_asset",
    "art_analysis_results_asset", 
    "final_dataset_asset",
    
    # Caption generation
    "image_selection_asset",
    "provider_selection_asset",
    "caption_generation_asset",
    
    # Dataset management
    "dataset_metadata_asset",
    "dataset_verification_asset",
    "huggingface_upload_asset",
    "dataset_download_asset",
    "dataset_validation_asset"
]
