"""
# SPDX-License-Identifier: Apache-2.0
graphcap.io.nodes.copy_images

Provides node implementation for copying images to a target directory.

Key features:
- Batch image copying
- Directory structure preservation
- Progress tracking
- Error handling
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from loguru import logger
from tqdm import tqdm

from ...dag.node import BaseNode


class CopyImagesNode(BaseNode):
    """
    Node for copying images to a target directory.

    Handles batch copying of images while preserving directory structure
    and providing progress tracking.
    """

    @classmethod
    def schema(cls) -> Dict[str, Dict[str, Any]]:
        """Define node schema."""
        return {
            "required": {
                "image_paths": {
                    "type": "LIST[PATH]",
                    "description": "List of paths to images to copy",
                },
                "target_dir": {
                    "type": "STRING",
                    "description": "Target directory for copied images",
                },
            },
            "optional": {
                "preserve_structure": {
                    "type": "BOOL",
                    "default": False,
                    "description": "Preserve source directory structure",
                },
                "batch_timestamp": {
                    "type": "STRING",
                    "description": "Timestamp for batch directory",
                    "default": datetime.now().strftime("%Y%m%d_%H%M%S"),
                },
            },
        }

    @property
    def outputs(self) -> Dict[str, str]:
        """Define node outputs."""
        return {
            "copied_paths": "LIST[PATH]",
            "copy_info": "DICT",
        }

    @property
    def category(self) -> str:
        """Define node category."""
        return "IO"

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute image copying."""
        self.validate_inputs(**kwargs)

        image_paths = kwargs["image_paths"]
        target_base = Path(kwargs["target_dir"])
        preserve_structure = kwargs.get("preserve_structure", False)
        timestamp = kwargs.get("batch_timestamp", datetime.now().strftime("%Y%m%d_%H%M%S"))

        # Create batch directory with timestamp
        target_dir = target_base / f"batch_{timestamp}" / "images"
        target_dir.mkdir(parents=True, exist_ok=True)

        copied_paths: List[Path] = []
        failed_copies: List[Dict[str, str]] = []
        total_size = 0

        logger.info(f"Copying {len(image_paths)} images to {target_dir}")

        for src_path in tqdm(image_paths, desc="Copying images"):
            try:
                src_path = Path(src_path)
                if preserve_structure:
                    # Preserve directory structure relative to common parent
                    rel_path = src_path.parent.relative_to(src_path.parent.parent)
                    dst_path = target_dir / rel_path / src_path.name
                else:
                    dst_path = target_dir / src_path.name

                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dst_path)

                copied_paths.append(dst_path)
                total_size += dst_path.stat().st_size

            except Exception as e:
                logger.error(f"Failed to copy {src_path}: {e}")
                failed_copies.append({"source": str(src_path), "error": str(e)})

        # Prepare copy info
        copy_info = {
            "timestamp": timestamp,
            "target_dir": str(target_dir),
            "total_copied": len(copied_paths),
            "total_failed": len(failed_copies),
            "total_size_bytes": total_size,
            "failed_copies": failed_copies,
            "preserve_structure": preserve_structure,
        }

        logger.info(f"Copied {len(copied_paths)} images ({total_size / 1024 / 1024:.2f} MB)")
        if failed_copies:
            logger.warning(f"Failed to copy {len(failed_copies)} images")

        return {"copied_paths": copied_paths, "copy_info": copy_info}
