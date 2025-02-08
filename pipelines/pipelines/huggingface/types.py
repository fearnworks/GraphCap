# SPDX-License-Identifier: Apache-2.0
"""Type definitions for Hugging Face assets."""

from typing import List, TypedDict

import dagster as dg


class DatasetMetadata(TypedDict):
    """Type definition for dataset metadata."""

    # Define the structure of your dataset metadata here
    pass  # Replace with actual fields


class DatasetExportManifestMetadata(TypedDict):
    """Type definition for dataset export manifest metadata."""

    export_dir: str
    manifest_path: str


class HfUploadManifestMetadata(TypedDict):
    """Type definition for Hugging Face upload manifest metadata."""

    dataset_name: str
    namespace: str
    dataset_url: str


class HfUploadManifestConfig(dg.Config):
    """Configuration schema for the huggingface_upload_manifest asset."""

    dataset_name: str
    namespace: str
    dataset_description: str
    dataset_tags: List[str]
    include_images: bool = True
    use_hf_urls: bool = False
    private_dataset: bool = False
