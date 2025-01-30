"""
# SPDX-License-Identifier: Apache-2.0
Dataset Metadata Module

This module handles the creation and management of dataset metadata,
including configuration, metadata entries, and dataset cards.

Classes:
    DatasetConfig: Configuration model for dataset properties
    DatasetMetadataHandler: Handler for metadata operations
"""

from typing import List

from pydantic import BaseModel


class DatasetConfig(BaseModel):
    """
    Configuration model for dataset properties.

    Attributes:
        name (str): Name of the dataset
        description (str): Description of the dataset
        tags (List[str]): List of tags describing the dataset
        include_images (bool): Whether to include images in the dataset
        use_hf_urls (bool): Whether to use HuggingFace URLs for image paths
    """

    name: str
    description: str
    tags: List[str]
    include_images: bool = True
    use_hf_urls: bool = False


class DatasetMetadataHandler:
    """
    Handler for dataset metadata operations.

    Provides methods for creating standardized metadata entries,
    dataset configurations, and documentation.
    """

    def create_metadata_entry(self, entry: dict, relative_image_path: str) -> dict:
        """
        Create a standardized metadata entry from raw data.

        Args:
            entry (dict): Raw data entry containing caption information
            relative_image_path (str): Relative path to the image file

        Returns:
            dict: Standardized metadata entry with all required fields
        """
        """Create a standardized metadata entry from raw data"""
        return {
            "file_name": relative_image_path,
            "image": relative_image_path,
            "config_name": entry.get("config_name", ""),
            "version": entry.get("version", ""),
            "model": entry.get("model", ""),
            "provider": entry.get("provider", ""),
            "split": "default",
            "parsed": {
                "tags_list": entry.get("parsed", {}).get("tags_list", []),
                "short_caption": entry.get("parsed", {}).get("short_caption", ""),
                "verification": entry.get("parsed", {}).get("verification", ""),
                "dense_caption": entry.get("parsed", {}).get("dense_caption", ""),
            },
        }

    def create_data_config(self) -> dict:
        """
        Create the dataset configuration structure.

        Returns:
            dict: Dataset configuration with default settings
        """
        """Create the dataset configuration structure"""
        return {
            "configs": [{"config_name": "default", "data_files": [{"split": "default", "path": "data/metadata.jsonl"}]}]
        }

    def create_dataset_metadata(self, splits: List[str], column_names: List[str]) -> dict:
        """
        Create the dataset metadata structure.

        Args:
            splits (List[str]): List of dataset split names
            column_names (List[str]): List of column names in the dataset

        Returns:
            dict: Dataset metadata structure
        """
        """Create the dataset metadata structure"""
        return {
            "splits": splits,
            "column_names": column_names,
        }

    def create_dataset_card(self, config: DatasetConfig, num_examples: int) -> str:
        """
        Generate the dataset card/README content.

        Args:
            config (DatasetConfig): Dataset configuration
            num_examples (int): Number of examples in the dataset

        Returns:
            str: Markdown formatted dataset card content
        """
        """Generate the dataset card/README content"""
        return f"""---
language:
  - en
license: cc0-1.0
pretty_name: {config.name}
dataset_info:
  features:
    - name: file_name
      dtype: string
    - name: image
      dtype: image
    - name: config_name
      dtype: string
    - name: version
      dtype: string
    - name: model
      dtype: string
    - name: provider
      dtype: string
    - name: parsed
      struct:
        - name: tags_list
          sequence: string
        - name: short_caption
          dtype: string
        - name: verification
          dtype: string
        - name: dense_caption
          dtype: string
  splits:
    - name: default
      num_examples: {num_examples}
  download_size: null
  dataset_size: null
configs:
  - config_name: default
    data_files:
      - split: default
        path: data/metadata.jsonl
tags:
  - image-to-text
  - computer-vision
  - image-captioning
{chr(10).join([f"  - {tag}" for tag in config.tags])}
---

# {config.name}

{config.description}

## Dataset Structure

The dataset contains images with associated metadata including captions, tags, and verification information.
"""
