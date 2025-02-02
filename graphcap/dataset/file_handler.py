"""
# SPDX-License-Identifier: Apache-2.0
Dataset File Handler Module

This module provides functionality for handling file operations related to datasets, including:
- Exporting data to JSONL format
- Managing work session persistence
- Handling image file paths and references

Classes:
    DatasetFileHandler: Handles file operations for dataset management
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger


class DatasetFileHandler:
    """
    Handles file operations for dataset management.

    This class provides methods for saving and loading dataset files,
    managing work sessions, and handling file paths for dataset resources.

    Attributes:
        export_dir (Path): Base directory for exporting files and saving work sessions
    """

    def __init__(self, export_dir: Path):
        """
        Initialize the DatasetFileHandler.

        Args:
            export_dir: Base directory path for file operations
        """
        self.export_dir = Path(export_dir)
        logger.info(f"DatasetFileHandler initialized with export directory: {self.export_dir}")
        self.export_dir.mkdir(parents=True, exist_ok=True)

    async def export_to_jsonl(
        self,
        captions: List[Dict],
        output_path: Optional[Path] = None,
        use_hf_urls: bool = False,
        repo_id: Optional[str] = None,
    ) -> Path:
        """
        Export caption data to JSONL format.

        Args:
            captions: List of caption dictionaries to export
            output_path: Optional custom output path, defaults to export_dir/captions.jsonl
            use_hf_urls: Whether to use HuggingFace URLs for image paths
            repo_id: HuggingFace repository ID (required if use_hf_urls is True)

        Returns:
            Path: Path to the exported JSONL file

        Raises:
            IOError: If unable to write to the output file
            TypeError: If captions contain non-serializable data
            ValueError: If use_hf_urls is True but repo_id is not provided
        """
        if output_path is None:
            output_path = self.export_dir / "captions.jsonl"

        if use_hf_urls and not repo_id:
            raise ValueError("repo_id must be provided when use_hf_urls is True")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w") as f:
            for caption in captions:
                # Create a copy to avoid modifying the original
                caption_copy = caption.copy()

                # Convert filename to appropriate format
                if "filename" in caption_copy:
                    orig_path = Path(caption_copy["filename"])
                    if use_hf_urls:
                        # Format: https://huggingface.co/datasets/{repo_id}/raw/main/data/images/{filename}
                        caption_copy["filename"] = (
                            f"https://huggingface.co/datasets/{repo_id}/raw/main/data/images/{orig_path.name}"
                        )
                    else:
                        # Use relative path
                        caption_copy["filename"] = f"./images/{orig_path.name}"

                f.write(json.dumps(caption_copy) + "\n")

        logger.info(f"Exported {len(captions)} captions to {output_path}")
        return output_path

    async def save_work_session(self, session_data: Dict, session_id: str) -> Path:
        """
        Save a work session to disk.

        Args:
            session_data: Dictionary containing session data to save
            session_id: Unique identifier for the session

        Returns:
            Path: Path to the saved session file

        Raises:
            TypeError: If session_data contains non-JSON-serializable objects
            IOError: If unable to write to the session file
        """
        session_path = self.export_dir / f"session_{session_id}.json"
        with session_path.open("w") as f:
            json.dump(session_data, f)
        return session_path

    async def load_work_session(self, session_id: str) -> Optional[Dict]:
        """
        Load a previously saved work session.

        Args:
            session_id: Unique identifier for the session to load

        Returns:
            Optional[Dict]: Session data if found, None if session doesn't exist

        Raises:
            json.JSONDecodeError: If session file contains invalid JSON
        """
        session_path = self.export_dir / f"session_{session_id}.json"
        if session_path.exists():
            with session_path.open() as f:
                return json.load(f)
        return None

    def get_image_path(self, input_dir: Path, filename: str) -> Path:
        """
        Get the full path for an image file.

        Args:
            input_dir: Base directory containing images
            filename: Relative path or filename of the image

        Returns:
            Path: Full path to the image file

        Note:
            Handles filenames that may start with './' by stripping the prefix
        """
        return input_dir / filename.lstrip("./")
