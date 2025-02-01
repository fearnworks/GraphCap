"""
# SPDX-License-Identifier: Apache-2.0
graphcap.dataset.nodes.export

Node for exporting perspective results to dataset format.

Key features:
- Converts perspective outputs to dataset format
- Handles multiple perspectives
- Organizes metadata and files
- Prepares for HuggingFace upload
"""

import os
from pathlib import Path
from typing import Any, Dict

from loguru import logger

from ...dag.node import BaseNode
from ..dataset_manager import DatasetManager
from ..metadata import DatasetConfig


class DatasetExportNode(BaseNode):
    """
    Node for exporting perspective results to dataset format.

    Converts perspective outputs into a structured dataset format
    suitable for training or sharing on HuggingFace Hub.
    """

    @classmethod
    def outputs(cls) -> Dict[str, Any]:
        """Define node outputs."""
        return {
            "dataset_path": {
                "type": "STRING",
                "description": "Path to exported dataset JSONL file",
            },
            "dataset_url": {
                "type": "STRING",
                "description": "HuggingFace dataset URL if uploaded",
                "optional": True,
            },
        }

    @classmethod
    def schema(cls) -> Dict[str, Dict[str, Any]]:
        """Define node schema."""
        return {
            "required": {
                "output_paths": {
                    "type": "DICT",
                    "description": "Paths to perspective outputs",
                },
                "batch_dir": {
                    "type": "STRING",
                    "description": "Base directory containing outputs",
                },
                "dataset_config": {
                    "type": "DICT",
                    "description": "Dataset configuration",
                    "properties": {
                        "name": {"type": "STRING", "description": "Dataset name"},
                        "description": {"type": "STRING", "description": "Dataset description"},
                        "tags": {"type": "LIST", "description": "Dataset tags"},
                        "include_images": {"type": "BOOL", "description": "Whether to include images"},
                    },
                },
            },
            "optional": {
                "push_to_hub": {
                    "type": "BOOL",
                    "description": "Whether to upload to HuggingFace Hub",
                    "default": False,
                },
                "hf_token_env": {
                    "type": "STRING",
                    "description": "Environment variable name for HuggingFace API token",
                    "default": "HUGGING_FACE_HUB_TOKEN",
                },
                "private": {
                    "type": "BOOL",
                    "description": "Whether to create private repository",
                    "default": False,
                },
            },
        }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute dataset export."""
        self.validate_inputs(**kwargs)

        # Initialize dataset manager
        batch_dir = Path(kwargs["batch_dir"])
        export_dir = batch_dir / "dataset"
        dataset_manager = DatasetManager(export_dir)

        # Create dataset config
        config = DatasetConfig(**kwargs["dataset_config"])

        # Convert perspective outputs to dataset format
        captions = []
        output_paths = kwargs["output_paths"]

        for path_key, path in output_paths.items():
            if path_key.endswith("_formal"):
                # Extract perspective type
                perspective_type = path_key.replace("_formal", "")

                # Read formal analysis
                formal_path = Path(path)
                formal_content = formal_path.read_text()

                # Get associated image path
                image_path = output_paths.get("image", "")

                # Create caption entry
                caption = {
                    "filename": str(image_path),
                    "perspective": perspective_type,
                    "formal_analysis": formal_content,
                    "config_name": "default",
                    "version": "1.0",
                    "provider": "gemini",
                    "parsed": {
                        "formal_analysis": formal_content,
                    },
                }
                captions.append(caption)

        # Export to JSONL
        jsonl_path = await dataset_manager.export_to_jsonl(captions)
        logger.info(f"Exported {len(captions)} captions to {jsonl_path}")

        # Upload to HuggingFace if requested
        if kwargs.get("push_to_hub"):
            # Get token from environment
            token_env = kwargs.get("hf_token_env", "HUGGING_FACE_HUB_TOKEN")
            token = os.getenv(token_env)

            if not token:
                logger.warning(f"HuggingFace token not found in environment variable: {token_env}")
                return {"dataset_path": str(jsonl_path)}

            hf_url = await dataset_manager.create_hf_dataset(
                jsonl_path=jsonl_path,
                config=config,
                push_to_hub=True,
                token=token,
                private=kwargs.get("private", False),
            )
            logger.info(f"Uploaded dataset to {hf_url}")
            return {"dataset_url": hf_url}

        return {"dataset_path": str(jsonl_path)}
