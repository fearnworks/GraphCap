"""
# SPDX-License-Identifier: Apache-2.0
Graph Report Generator

Provides functionality for generating HTML reports from graph captions
using Jinja2 templates.
"""

from pathlib import Path
from typing import Sequence

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .types import CaptionData

# Initialize Jinja2 environment
env = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"), autoescape=select_autoescape(["html", "xml"])
)


def generate_graph_report(captions: Sequence[CaptionData], job_dir: Path) -> None:
    """
    Generate an HTML report for graph captions.


    Args:
        captions: List of caption data dictionaries
        job_dir: Directory to write the report to
    """
    template = env.get_template("graph_report.html")

    # Check if images directory exists
    images_dir = job_dir / "images"

    # Process captions for template
    processed_captions = []
    for caption in captions:
        # Group tags by category
        tags_by_category = {}
        for tag in caption["parsed"]["tags_list"]:
            category = tag["category"]
            if category not in tags_by_category:
                tags_by_category[category] = []
            tags_by_category[category].append(tag)

        # Use copied image if available, otherwise use original path
        image_name = Path(caption["filename"]).name
        relative_path = f"images/{image_name}" if images_dir.exists() else str(caption["filename"])

        processed_captions.append(
            {
                "image_path": relative_path,
                "short_caption": caption["parsed"]["short_caption"],
                "tags_by_category": tags_by_category,
                "verification": caption["parsed"]["verification"],
                "dense_caption": caption["parsed"]["dense_caption"],
            }
        )

    # Render and write HTML
    html_content = template.render(captions=processed_captions)
    report_file = job_dir / "graph_report.html"
    report_file.write_text(html_content)
