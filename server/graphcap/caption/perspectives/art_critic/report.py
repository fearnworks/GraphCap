"""
# SPDX-License-Identifier: Apache-2.0
Art Critic Report Generator

Provides functionality for generating HTML reports from art critic analysis
using Jinja2 templates and formal analysis principles.
"""

from collections.abc import Sequence
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .types import CaptionData, CaptionDict

# Initialize Jinja2 environment
env = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"), autoescape=select_autoescape(["html", "xml"])
)


def generate_art_report(captions: Sequence[CaptionDict], job_dir: Path) -> None:
    """
    Generate an HTML report for art critic analysis.

    Args:
        captions: Sequence of caption data dictionaries containing formal analysis
        job_dir: Directory to write the report to
    """
    template = env.get_template("art_report.html")

    # Check if images directory exists
    images_dir = job_dir / "images"

    # Process captions for template
    processed_captions: list[CaptionData] = []
    for caption in captions:
        # Use copied image if available, otherwise use original path
        image_name = Path(caption["filename"]).name
        relative_path = f"images/{image_name}" if images_dir.exists() else str(caption["filename"])

        processed_captions.append(
            {
                "image_path": relative_path,
                "visual_elements": caption["parsed"]["visual_elements"],
                "technical_elements": caption["parsed"]["technical_elements"],
                "style_elements": caption["parsed"]["style_elements"],
                "formal_tags": caption["parsed"]["formal_tags"],
                "formal_analysis": caption["parsed"]["formal_analysis"],
            }
        )

    # Render and write HTML
    html_content = template.render(captions=processed_captions)
    report_file = job_dir / "art_report.html"
    _ = report_file.write_text(html_content)  # Assign unused result to _
