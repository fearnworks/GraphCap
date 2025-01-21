# prompt_config_library.py

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class CaptionMode(Enum):
    DESCRIPTIVE = "descriptive"
    TRAINING = "training"
    MIDJOURNEY = "midjourney"
    BOORU_TAGS = "booru_tags"
    BOORU_LIKE_TAGS = "booru_like_tags"
    ART_CRITIC = "art_critic"
    PRODUCT_LISTING = "product_listing"
    SOCIAL_MEDIA = "social_media"


class ToneStyle(Enum):
    FORMAL = "formal"
    CASUAL = "casual"


@dataclass
class PromptConfig:
    config_name: str
    mode: CaptionMode = CaptionMode.DESCRIPTIVE
    tone: ToneStyle = ToneStyle.FORMAL
    word_count: Optional[int] = None
    length: Optional[str] = None  # e.g., "short", "long", "detailed"
    character_name: Optional[str] = None
    use_case: Optional[str] = None
    description: Optional[str] = None

    # Extra options flags
    exclude_unchangeable_attributes: bool = False
    include_lighting: bool = False
    include_camera_angle: bool = False
    include_watermark_info: bool = False
    include_artifact_info: bool = False
    include_camera_details: bool = False
    keep_pg: bool = False
    exclude_resolution: bool = True
    include_quality_assessment: bool = False
    include_composition: bool = False
    exclude_text: bool = True
    include_depth_of_field: bool = False
    include_lighting_source: bool = False
    avoid_ambiguity: bool = True
    include_sfw_rating: bool = False
    only_important_elements: bool = True


class PromptConfigLibrary:
    """Library of preset prompt configurations for artistic image captioning."""

    @staticmethod
    def get_artistic_configs() -> List[PromptConfig]:
        """Get a list of artistic prompt configurations."""
        return [
            PromptConfig(
                config_name="booru_tags_composition",
                mode=CaptionMode.BOORU_TAGS,
                tone=ToneStyle.FORMAL,
                include_composition=True,
                include_lighting=True,
                exclude_resolution=True,
                use_case="Booru Tags for Composition Analysis",
                description="Generates Booru tags highlighting composition and lighting aspects of the image."
            ),
            PromptConfig(
                config_name="in_depth_art_critique",
                mode=CaptionMode.ART_CRITIC,
                include_composition=True,
                include_lighting=True,
                include_quality_assessment=True,
                include_depth_of_field=True,
                include_lighting_source=True,
                avoid_ambiguity=True,
                exclude_text=True,
                use_case="In-depth Art Critique",
                description="An in-depth art critique including composition, lighting, quality assessment, depth of field, and lighting source, avoiding ambiguity."
            ),
            PromptConfig(
                config_name="artistic_training_prompt",
                mode=CaptionMode.TRAINING,
                include_lighting=True,
                include_composition=True,
                include_depth_of_field=True,
                exclude_text=True,
                avoid_ambiguity=True,
                use_case="Artistic AI Training Data",
                description="A training prompt including artistic elements like lighting, composition, depth of field, avoiding ambiguity, and excluding text."
            ),
            PromptConfig(
                config_name="descriptive_formal_detailed",
                mode=CaptionMode.DESCRIPTIVE,
                tone=ToneStyle.FORMAL,
                length="detailed",
                include_lighting=True,
                include_composition=True,
                exclude_text=True,
                avoid_ambiguity=True,
                use_case="Detailed Artistic Description",
                description="A detailed formal description including lighting and composition, avoiding ambiguity and excluding text."
            ),
            PromptConfig(
                config_name="art_critic_detailed",
                mode=CaptionMode.ART_CRITIC,
                include_composition=True,
                include_lighting=True,
                include_quality_assessment=True,
                exclude_text=True,
                use_case="Detailed Art Critic Analysis",
                description="A detailed art critic analysis including composition, lighting, and quality assessment, excluding text."
            ),
            PromptConfig(
                config_name="technical_photo_analysis",
                mode=CaptionMode.DESCRIPTIVE,
                tone=ToneStyle.FORMAL,
                include_camera_details=True,
                include_lighting=True,
                include_depth_of_field=True,
                include_composition=True,
                exclude_text=True,
                use_case="Technical Photo Analysis",
                description="Technical analysis including camera details, lighting, depth of field, composition, excluding text."
            ),
            PromptConfig(
                config_name="artistic_midjourney_detailed",
                mode=CaptionMode.MIDJOURNEY,
                tone=ToneStyle.CASUAL,
                length="detailed",
                include_composition=True,
                include_lighting=True,
                include_depth_of_field=True,
                exclude_text=True,
                use_case="Detailed MidJourney Prompt",
                description="Provides detailed MidJourney prompts incorporating composition, lighting, and depth of field."
            ),
        ]

    @staticmethod
    def get_config_by_name(name: str) -> PromptConfig:
        """Retrieve a prompt configuration by its name."""
        configs = PromptConfigLibrary.get_artistic_configs()
        for config in configs:
            if config.config_name == name:
                return config
        raise ValueError(f"No config found with name '{name}'")
