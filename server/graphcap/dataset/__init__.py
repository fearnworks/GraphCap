"""
# SPDX-License-Identifier: Apache-2.0
Dataset Module

This module provides functionality for managing image datasets with captions and metadata.
It handles dataset creation, export, and upload to Hugging Face Hub.

Key features:
- Dataset creation and management
- File handling and persistence
- HuggingFace Hub integration
- Metadata generation and validation

Directory Structure:
    When uploaded to HuggingFace Hub, graphcapdatasets follow this structure:

    dataset_name/
    ├── README.md                  # Dataset card with description and usage
    ├── dataset-metadata.json      # Dataset metadata and configuration
    └── data/
        ├── config.yaml           # Dataset split configuration
        ├── metadata.jsonl        # Image metadata and captions
        ├── captions.jsonl        # Raw caption data
        └── images/              # Image files (if include_images=True)
            ├── image1.jpg
            ├── image2.jpg
            └── ...

Files:
    - README.md: Contains dataset description, usage examples, and citation info
    - dataset-metadata.json: Technical metadata about features and splits
    - config.yaml: Configuration for dataset splits and file paths
    - metadata.jsonl: Structured metadata for each image including captions
    - captions.jsonl: Raw caption data from vision models
    - images/: Directory containing the original images (optional)

Note:
    Image paths in metadata.jsonl and captions.jsonl are relative to the data/
    directory using the format "./images/filename.jpg"
"""
