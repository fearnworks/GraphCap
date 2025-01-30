"""
# SPDX-License-Identifier: Apache-2.0
Art Critic Caption Module

Provides artistic analysis of images focusing on formal analysis and
concrete visual elements, following ArtCoT methodology for reduced hallucination.
"""

from typing import List

from pydantic import BaseModel, Field

from .base_caption import BaseCaptionProcessor


class ArtCriticData(BaseModel):
    """Schema for art critic analysis response following formal analysis principles."""

    # Visual Elements Analysis
    visual_elements: List[str] = Field(
        description="Concrete visual elements present in the image (colors, shapes, lines, etc.)"
    )

    # Technical Analysis
    technical_elements: List[str] = Field(
        description="Observable technical aspects (lighting, perspective, composition, etc.)"
    )

    # Style Analysis
    style_elements: List[str] = Field(description="Identifiable style characteristics and artistic techniques")

    # Formal Tags
    formal_tags: List[str] = Field(description="Objective descriptive tags based on formal analysis")

    # Overall Analysis
    formal_analysis: str = Field(description="Concrete analysis connecting visual elements to artistic principles")


instruction = """Analyze this image using formal analysis principles, focusing on observable elements:

1. Visual Elements: Identify concrete visual elements present in the image:
- Colors and their relationships
- Shapes and forms
- Lines and textures
- Space and scale

2. Technical Elements: Document observable technical aspects:
- Lighting and shadows
- Perspective and depth
- Composition and layout
- Execution quality

3. Style Elements: Note identifiable artistic techniques:
- Brushwork or medium characteristics
- Stylistic choices
- Technical approaches
- Artistic methods

Create objective descriptive tags based on your observations.
Provide a formal analysis that connects these elements to artistic principles.
Use concrete, observable language - only describe what you can definitively see."""


class ArtCriticProcessor(BaseCaptionProcessor):
    """
    Processor for generating formal analysis of images.

    Uses ArtCoT methodology to reduce hallucination and improve
    alignment with human aesthetic judgment through concrete
    observation and formal analysis.
    """

    def __init__(self):
        super().__init__(
            config_name="artcritic",
            version="1",
            prompt=instruction,
            schema=ArtCriticData,
        )
