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
    def schema(cls) -> Dict[str, Dict[str, Any]]:
        """Define node schema."""
        return {
            "required": {
                "perspective_results": {
                    "type": "LIST",
                    "description": "List of perspective results from analysis nodes",
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

    @property
    def outputs(self) -> Dict[str, str]:
        """Define node outputs."""
        return {
            "dataset_path": "STRING",
            "dataset_url": "STRING",
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

        # Convert perspective results to dataset format
        captions = []
        for result in kwargs["perspective_results"]:
            if not isinstance(result, dict) or "filename" not in result:
                logger.warning(f"Skipping invalid result: {result}")
                continue

            caption = {
                "filename": result["filename"],
                "config_name": result.get("config_name", ""),
                "version": result.get("version", ""),
                "model": result.get("model", ""),
                "provider": result.get("provider", ""),
                "parsed": result.get("parsed", {}),
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
            return {"dataset_path": str(jsonl_path), "dataset_url": hf_url}

        return {"dataset_path": str(jsonl_path)}
