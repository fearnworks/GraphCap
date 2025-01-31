# SPDX-License-Identifier: Apache-2.0

"""
Graph Caption Module

Provides structured analysis of images with categorized tags and descriptions.
Focuses on comprehensive scene understanding and detailed content analysis.
"""

from typing import Any, Dict, List

from loguru import logger
from pydantic import BaseModel, Field
from rich.table import Table

from .base_caption import BaseCaptionProcessor


class Tag(BaseModel):
    """Model for individual tagged elements in the image."""

    tag: str = Field(description="Description of the tagged element")
    category: str = Field(description="Category the tag belongs to")
    confidence: float = Field(description="Confidence score between 0 and 1", gt=0, le=1)


class GraphCaptionData(BaseModel):
    """Schema for structured graph caption response."""

    tags_list: List[Tag] = Field(description="List of categorized tags with confidence scores")
    short_caption: str = Field(description="Concise single sentence caption (max 100 chars)")
    verification: str = Field(description="Verification of tag accuracy and visual grounding")
    dense_caption: str = Field(description="Detailed narrative description incorporating tagged elements")


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
    },
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


class GraphCaptionProcessor(BaseCaptionProcessor):
    """
    Processor for generating structured graph captions.

    Provides comprehensive scene analysis with categorized tags,
    verification, and multiple caption formats.
    """

    def __init__(self):
        super().__init__(
            config_name="graphcap",
            version="1",
            prompt=instruction,
            schema=GraphCaptionData,
        )

    def create_rich_table(self, caption_data: Dict[str, Any]) -> Table:
        """Create Rich table for graph caption data."""
        result = caption_data["parsed"]

        # Create main table
        table = Table(show_header=True, header_style="bold magenta", expand=True)
        table.add_column("Category", style="cyan")
        table.add_column("Content", style="green")

        # Add short caption
        table.add_row("Short Caption", result["short_caption"])

        # Group tags by category
        tags_by_category = {}
        for tag in result["tags_list"]:
            category = tag["category"]
            if category not in tags_by_category:
                tags_by_category[category] = []
            tags_by_category[category].append(f"• {tag['tag']} ({tag['confidence']:.2f})")

        # Add tags section
        tags_content = []
        for category, tags in tags_by_category.items():
            tags_content.append(f"[bold]{category}[/bold]")
            tags_content.extend(tags)
            tags_content.append("")  # Add spacing between categories

        table.add_row("Tags", "\n".join(tags_content))

        # Add verification
        table.add_row("Verification", result["verification"])

        table.add_row("Dense Caption", result["dense_caption"])
        logger.info(result["dense_caption"])
        return table
