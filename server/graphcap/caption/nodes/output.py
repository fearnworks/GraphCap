"""
# SPDX-License-Identifier: Apache-2.0
graphcap.caption.nodes.output

Output management node for perspective results.

Key features:
- Handles multiple perspective outputs
- Manages output formats and directories
- Organizes outputs by perspective type
- Copies associated images if needed
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from loguru import logger

from ...dag.node import BaseNode


class PerspectiveOutputNode(BaseNode):
    """
    Node for managing perspective output storage.

    Handles saving multiple perspective results to configured output formats and locations.
    Manages file organization and optional image copying.
    """

    @classmethod
    def schema(cls) -> Dict[str, Dict[str, Any]]:
        """Define node schema."""
        return {
            "required": {
                "perspective_results": {
                    "type": "DICT",
                    "description": "Results from perspective processing",
                },
                "output": {
                    "type": "DICT",
                    "description": "Output configuration",
                    "properties": {
                        "directory": {"type": "STRING", "description": "Base output directory"},
                        "formats": {"type": "LIST", "description": "Output formats to generate"},
                        "store_logs": {"type": "BOOL", "description": "Whether to store process logs"},
                        "copy_images": {"type": "BOOL", "description": "Whether to copy source images"},
                    },
                },
            },
            "optional": {
                "batch_timestamp": {
                    "type": "STRING",
                    "description": "Timestamp for batch directory",
                    "default": datetime.now().strftime("%Y%m%d_%H%M%S"),
                },
                "perspective_type": {
                    "type": "STRING",
                    "description": "Type of perspective (art, graph, etc)",
                    "default": "unknown",
                },
            },
        }

    @classmethod
    def outputs(cls) -> Dict[str, Any]:
        """Define node outputs."""
        return {
            "output_paths": {
                "type": "DICT",
                "description": "Paths to generated output files",
            },
        }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute output management."""
        self.validate_inputs(**kwargs)

        results = kwargs["perspective_results"]
        output_config = kwargs["output"]
        timestamp = kwargs.get("batch_timestamp", datetime.now().strftime("%Y%m%d_%H%M%S"))
        perspective_type = kwargs.get("perspective_type", "unknown")

        # Create batch directory structure
        base_dir = Path(output_config["directory"])
        batch_dir = base_dir / f"batch_{timestamp}"
        perspective_dir = batch_dir / perspective_type
        perspective_dir.mkdir(parents=True, exist_ok=True)

        output_paths = {}

        # Save outputs in requested formats
        for fmt in output_config["formats"]:
            if fmt in results:
                # Create format-specific directory if needed
                format_dir = perspective_dir / fmt
                format_dir.mkdir(exist_ok=True)

                output_file = format_dir / results[fmt]["filename"]
                output_file.write_text(results[fmt]["content"])
                output_paths[f"{perspective_type}_{fmt}"] = str(output_file)
                logger.info(f"Saved {perspective_type} {fmt} output to {output_file}")

        # Copy images if requested
        if output_config.get("copy_images"):
            images_dir = batch_dir / "images"
            images_dir.mkdir(exist_ok=True)

            if "image_path" in results:
                src_path = Path(results["image_path"])
                dst_path = images_dir / src_path.name
                shutil.copy2(src_path, dst_path)
                output_paths["image"] = str(dst_path)
                logger.info(f"Copied image to {dst_path}")

        # Store process logs if requested
        if output_config.get("store_logs") and "logs" in results:
            log_dir = perspective_dir / "logs"
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / "process.log"
            log_file.write_text(results["logs"])
            output_paths[f"{perspective_type}_logs"] = str(log_file)
            logger.info(f"Saved {perspective_type} process logs to {log_file}")

        return {"output_paths": output_paths, "batch_dir": str(batch_dir), "perspective_dir": str(perspective_dir)}
