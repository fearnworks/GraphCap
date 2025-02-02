"""
# SPDX-License-Identifier: Apache-2.0
Dataset Management Module

This module provides functionality for managing datasets, including:
- Exporting captions to JSONL format
- Creating and uploading datasets to Hugging Face Hub
- Managing work sessions for dataset creation
- Processing images and metadata

Classes:
    DatasetManager: Main class for dataset operations and management
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger

from graphcap.dataset.file_handler import DatasetFileHandler
from graphcap.dataset.hf_client import HuggingFaceClient
from graphcap.dataset.metadata import DatasetConfig, DatasetMetadataHandler


class DatasetManager:
    """
    Manages dataset operations including export, creation, and upload to Hugging Face Hub.

    This class coordinates between file handling, metadata management, and HuggingFace
    interactions to provide a complete dataset management solution.

    Attributes:
        export_dir (Path): Directory for exporting dataset files
        file_handler (DatasetFileHandler): Handles file operations
        hf_client (HuggingFaceClient): Client for HuggingFace operations
        metadata_handler (DatasetMetadataHandler): Handles metadata creation and validation
    """

    def __init__(
        self,
        export_dir: Path,
        file_handler: Optional[DatasetFileHandler] = None,
        hf_client: Optional[HuggingFaceClient] = None,
        metadata_handler: Optional[DatasetMetadataHandler] = None,
    ):
        self.export_dir = Path(export_dir)
        self.file_handler = file_handler or DatasetFileHandler(export_dir)
        self.hf_client = hf_client or HuggingFaceClient()
        self.metadata_handler = metadata_handler or DatasetMetadataHandler()

    async def export_to_jsonl(
        self,
        captions: List[Dict],
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Export captions to JSONL format.

        Args:
            captions: List of caption dictionaries to export
            output_path: Optional custom output path

        Returns:
            Path: Path to the exported JSONL file
        """
        return await self.file_handler.export_to_jsonl(captions, output_path)

    async def create_hf_dataset(
        self,
        jsonl_path: Path,
        config: DatasetConfig,
        push_to_hub: bool = False,
        token: Optional[str] = None,
        private: bool = False,
        use_hf_urls: bool = False,
        repo_id: Optional[str] = None,
    ) -> str:
        """
        Create and optionally upload a dataset to the Hugging Face Hub.

        Args:
            jsonl_path: Path to the JSONL file containing dataset
            config: Dataset configuration
            push_to_hub: Whether to upload to HuggingFace
            token: HuggingFace API token
            private: Whether to create a private repository
            use_hf_urls: Whether to use HuggingFace URLs for image paths
            repo_id: HuggingFace repository ID (required if use_hf_urls is True)

        Returns:
            str: Dataset path or HuggingFace URL

        Raises:
            Exception: If dataset creation or upload fails
        """
        if not push_to_hub or not token:
            return str(jsonl_path)

        try:
            # Get user info and create repo
            user_info = self.hf_client.get_user_info(token)
            username = user_info["name"]
            repo_id = f"{username}/{config.name}"

            logger.info(f"Creating dataset repository for user: {username}")
            self.hf_client.create_dataset_repo(repo_id, token, private)

            # Add delay and verify
            time.sleep(2)
            self.hf_client.verify_repo_exists(repo_id, token)

            # Load captions from input file
            captions = []
            with jsonl_path.open() as f:
                for line in f:
                    captions.append(json.loads(line))

            # Export captions with appropriate URLs
            output_path = await self.file_handler.export_to_jsonl(
                captions, output_path=jsonl_path, use_hf_urls=use_hf_urls, repo_id=repo_id
            )

            # Upload initial JSONL
            self.hf_client.upload_file(str(output_path), "data/captions.jsonl", repo_id, token)

            metadata_entries = []
            if config.include_images:
                metadata_entries = await self._process_images(jsonl_path, repo_id, token)

            # Upload metadata and configs
            await self._upload_metadata_files(repo_id, token, config, metadata_entries)

            return f"https://huggingface.co/datasets/{repo_id}"

        except Exception as e:
            logger.error(f"Error creating dataset: {e}")
            raise

    async def _process_images(self, jsonl_path: Path, repo_id: str, token: str) -> List[Dict]:
        """
        Process and upload images from the dataset.

        Args:
            jsonl_path: Path to JSONL file containing image references
            repo_id: HuggingFace repository ID
            token: HuggingFace API token

        Returns:
            List[Dict]: List of metadata entries for processed images
        """
        metadata_entries = []
        input_dir = jsonl_path.parent

        with jsonl_path.open() as f:
            for line in f:
                entry = json.loads(line)
                if "filename" not in entry:
                    continue

                # Extract just the filename from either local path or HF URL
                filename = Path(entry["filename"]).name
                image_path = self.file_handler.get_image_path(input_dir, filename)

                if not image_path.exists():
                    logger.warning(f"Image not found: {image_path}")
                    continue

                relative_path = f"images/{filename}"
                metadata_entries.append(self.metadata_handler.create_metadata_entry(entry, relative_path))

                try:
                    self.hf_client.upload_file(str(image_path), f"data/{relative_path}", repo_id, token)
                except Exception as e:
                    logger.warning(f"Failed to upload image {image_path}: {e}")

        return metadata_entries

    async def _upload_metadata_files(
        self, repo_id: str, token: str, config: DatasetConfig, metadata_entries: List[Dict]
    ):
        """
        Upload all metadata related files to HuggingFace.

        Args:
            repo_id: HuggingFace repository ID
            token: HuggingFace API token
            config: Dataset configuration
            metadata_entries: List of metadata entries
        """
        # Upload metadata.jsonl
        metadata_content = "\n".join(json.dumps(entry) for entry in metadata_entries)
        self.hf_client.upload_file(metadata_content.encode(), "data/metadata.jsonl", repo_id, token)

        # Upload config.yaml
        data_config = self.metadata_handler.create_data_config()
        self.hf_client.upload_file(json.dumps(data_config).encode(), "data/config.yaml", repo_id, token)

        # Upload dataset-metadata.json
        dataset_metadata = self.metadata_handler.create_dataset_metadata(
            splits=["default"],
            column_names=["file_name", "image", "config_name", "version", "model", "provider", "parsed"],
        )
        self.hf_client.upload_file(json.dumps(dataset_metadata).encode(), "dataset-metadata.json", repo_id, token)

        # Upload README.md
        readme_content = self.metadata_handler.create_dataset_card(config, len(metadata_entries))
        self.hf_client.upload_file(readme_content.encode(), "README.md", repo_id, token)

    async def save_work_session(self, session_data: Dict, session_id: str) -> Path:
        """
        Save current work session data.

        Args:
            session_data: Dictionary containing session data
            session_id: Unique identifier for the session

        Returns:
            Path: Path to the saved session file

        Raises:
            TypeError: If session data contains non-serializable objects
        """
        return await self.file_handler.save_work_session(session_data, session_id)

    async def load_work_session(self, session_id: str) -> Optional[Dict]:
        """
        Load a previous work session.

        Args:
            session_id: Unique identifier for the session

        Returns:
            Optional[Dict]: Session data if found, None otherwise
        """
        return await self.file_handler.load_work_session(session_id)
