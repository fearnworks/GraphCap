"""
# SPDX-License-Identifier: Apache-2.0
Graph Caption Processor

Implements structured analysis of images with categorized tags and descriptions.
"""

from pathlib import Path
from typing import Any

from loguru import logger
from rich.table import Table
from typing_extensions import override

from ..base import BasePerspective
from .network import generate_network_diagram
from .report import generate_graph_report
from .types import CaptionData, GraphCaptionData, ParsedData

instruction = """<Task>You are a structured image analysis agent. Generate comprehensive tag list, caption,
and dense caption for an image classification system.</Task>

<TagCategories requirement="You should generate a minimum of 1 tag for each category." confidence="Confidence score
for the tag, between 0 (exclusive) and 1 (inclusive).">
- Entity: The content of the image, including the objects, people, and other elements
- Relationship: The relationships between the entities in the image
- Style: The style of the image, including the color, lighting, and other stylistic elements
- Attribute: The most important attributes of the entities and relationships
- Composition: The composition of the image, including the arrangement of elements
- Contextual: The contextual elements including background and foreground
- Technical: The technical elements including camera angle and lighting
- Semantic: The semantic elements including meaning and symbols

<Examples note="These show the expected format as an abstraction.">
{
  "tags_list": [
    {
      "tag": "subject 1",
      "category": "Entity",
      "confidence": 0.98
    },
    {
      "tag": "subject 2",
      "category": "Entity",
      "confidence": 0.95
    },
    {
      "tag": "subject 1 runs from subject 2",
      "category": "Relationship",
      "confidence": 0.90
    }
  ]
}
</Examples>
</TagCategories>
<ShortCaption note="The short caption is a concise single sentence caption of the image content
with a maximum length of 100 characters.">
<Verification note="The verification identifies issues with the extracted tags and simple caption where the tags
do not match the visual content you can actually see. Be a critic.">
<DenseCaption note="The dense caption is a descriptive but grounded narrative paragraph of the image content.
Only reference items you are confident you can see in the image.It uses straightforward confident and clear language
without overt flowery prose. It incorporates elements from each of the tag categories to provide a broad dense caption">
"""


class GraphCaptionProcessor(BasePerspective):
    """
    Processor for generating structured graph captions.

    Provides comprehensive scene analysis with categorized tags,
    verification, and multiple caption formats.
    """

    def __init__(self) -> None:
        super().__init__(
            config_name="graphcap",
            version="1",
            prompt=instruction,
            schema=GraphCaptionData,
        )
        self._captions: list[CaptionData] = []

    @override
    def create_rich_table(self, caption_data: dict[str, ParsedData]) -> Table:
        """Create Rich table for graph caption data."""
        result = caption_data["parsed"]

        # Create main table
        table = Table(show_header=True, header_style="bold magenta", expand=True)
        table.add_column("Category", style="cyan")
        table.add_column("Content", style="green")

        # Add short caption
        table.add_row("Short Caption", result["short_caption"])

        # Group tags by category
        tags_by_category: dict[str, list[str]] = {}
        for tag in result["tags_list"]:
            if isinstance(tag, dict):
                category = str(tag["category"])
            else:
                category = tag.category

            if category not in tags_by_category:
                tags_by_category[category] = []

            confidence = tag["confidence"] if isinstance(tag, dict) else tag.confidence
            tag_text = tag["tag"] if isinstance(tag, dict) else tag.tag
            tags_by_category[category].append(f"• {tag_text} ({confidence:.2f})")

        # Add tags section
        tags_content: list[str] = []
        for category, tags in tags_by_category.items():
            tags_content.append(f"[bold]{category}[/bold]")
            tags_content.extend(tags)
            tags_content.append("")  # Add spacing between categories

        table.add_row("Tags", "\n".join(tags_content))
        table.add_row("Verification", result["verification"])
        table.add_row("Dense Caption", result["dense_caption"])
        logger.info(result["dense_caption"])
        return table

    @property
    @override
    def supported_formats(self) -> list[str]:
        return ["dense", "html", "network"]

    @override
    def write_format(self, format_name: str, job_dir: Path, caption_data: dict[str, Any]) -> None:
        if format_name == "dense":
            dense_file = job_dir / "dense_captions.txt"
            with dense_file.open("a") as f:
                _ = f.write(f"{caption_data['parsed']['dense_caption']}\n---\n")
        elif format_name == "html":
            # Store caption for batch HTML generation
            self._captions.append(
                {
                    "filename": str(caption_data["filename"]),
                    "input_path": str(caption_data["filename"]),
                    "parsed": caption_data["parsed"],
                }
            )  # type: ignore
            # Generate report after all captions are collected
            generate_graph_report(self._captions, job_dir)
        elif format_name == "network":
            # Store caption for network diagram
            self._captions.append(
                {
                    "filename": str(caption_data["filename"]),
                    "input_path": str(caption_data["filename"]),
                    "parsed": caption_data["parsed"],
                }
            )  # type: ignore
            # Generate network diagram after all captions are collected
            generate_network_diagram(self._captions, job_dir)
