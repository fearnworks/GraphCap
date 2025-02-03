"""
# SPDX-License-Identifier: Apache-2.0
Art Critic Processor

Provides artistic analysis of images focusing on formal analysis and
concrete visual elements, following ArtCoT methodology for reduced hallucination.
"""

from pathlib import Path
from typing import Any

from loguru import logger
from rich.table import Table
from typing_extensions import override

from ..base import BasePerspective
from .report import generate_art_report
from .types import ArtCriticResult, ArtCriticSchema, CaptionDict

instruction = """Analyze this image using formal analysis principles, focusing exclusively on observable elements.
 Avoid adding any subjective commentary or unnecessary filler details. Your response must follow this structured format:

1. Visual Elements: List only the concrete, observable elements present in the image:
   - Colors and their relationships
   - Shapes and forms
   - Lines and textures
   - Space and scale

2. Technical Elements: Document only the directly observable technical aspects:
   - Lighting and shadows
   - Perspective and depth
   - Composition and layout
   - Execution quality

3. Style Elements: Note only identifiable artistic techniques:
   - Brushwork or medium characteristics
   - Stylistic choices
   - Technical approaches
   - Artistic methods

4. Formal Tags: Provide a bullet list of objective, descriptive tags based solely on what is visible.

5. Formal Analysis: In a concise summary of no more than three sentences, connect the above elements to
artistic principles using only concrete, observable language. Do not speculate or include any additional commentary.

Only describe what you can definitively see."""


class ArtCriticProcessor(BasePerspective):
    """
    Processor for generating formal analysis of images.

    Uses ArtCoT methodology to reduce hallucination and improve
    alignment with human aesthetic judgment through concrete
    observation and formal analysis.
    """

    def __init__(self):
        super().__init__(
            config_name="artcap",
            version="1",
            prompt=instruction,
            schema=ArtCriticSchema,
        )
        self._captions: list[CaptionDict] = []

    @override
    def create_rich_table(self, caption_data: dict[str, ArtCriticResult]) -> Table:
        """Create Rich table for art critic data."""
        result = caption_data["parsed"]

        # Create main table
        table = Table(show_header=True, header_style="bold magenta", expand=True)
        table.add_column("Category", style="cyan")
        table.add_column("Elements", style="green")

        # Add each analysis section
        table.add_row("Visual Elements", "\n".join(f"• {element}" for element in result["visual_elements"]))
        table.add_row("Technical Elements", "\n".join(f"• {element}" for element in result["technical_elements"]))
        table.add_row("Style Elements", "\n".join(f"• {element}" for element in result["style_elements"]))
        table.add_row("Formal Tags", "\n".join(f"• {tag}" for tag in result["formal_tags"]))
        table.add_row("Formal Analysis", result["formal_analysis"])

        logger.info(f"Art analysis complete for {caption_data['filename']}")
        return table

    @property
    @override
    def supported_formats(self) -> list[str]:
        return ["html", "formal"]

    @override
    def write_format(self, format_name: str, job_dir: Path, caption_data: dict[str, Any]) -> None:
        """Write caption data in specified format.

        Args:
            format_name: Name of the output format
            job_dir: Directory to write output to
            caption_data: Caption data dictionary
        """
        if format_name == "html":
            # Store caption for batch HTML generation
            caption_dict = caption_data.copy()  # Make a copy to avoid modifying original
            caption_dict["input_path"] = caption_dict["filename"]
            self._captions.append(caption_dict)
            # Generate report after all captions are collected
            generate_art_report(self._captions, job_dir)
        elif format_name == "formal":
            formal_file = job_dir / "formal_analysis.txt"
            with formal_file.open("a") as f:
                f.write(f"{caption_data['parsed']['formal_analysis']}\n---\n")
