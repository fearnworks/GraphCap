from dataclasses import dataclass
from enum import Enum
from GraphCap.utils.logger import logger
from typing import Optional, List, Dict
from GraphCap.agents.joycap.prompt_config_library import PromptConfigLibrary, CaptionMode, ToneStyle, PromptConfig

@dataclass
class Prompt:
    prompt_config: PromptConfig
    config_name: str
    prompt: str
    weight: float


def build_base_prompt(config: PromptConfig) -> str:
    base = ""
    """Build the base prompt according to the caption mode"""
    if config.mode == CaptionMode.DESCRIPTIVE:
        base = f"Write a descriptive caption for this image in a {config.tone.value} tone"
    elif config.mode == CaptionMode.TRAINING:
        base = "Write a stable diffusion prompt for this image"
    elif config.mode == CaptionMode.MIDJOURNEY:
        base = "Write a MidJourney prompt for this image"
    elif config.mode == CaptionMode.BOORU_TAGS:
        base = "Write a list of Booru tags for this image"
    elif config.mode == CaptionMode.BOORU_LIKE_TAGS:
        base = "Write a list of Booru-like tags for this image"
    elif config.mode == CaptionMode.ART_CRITIC:
        base = "Analyze this image like an art critic would with information about its composition, style, symbolism, the use of color, light, any artistic movement it might belong to, etc"
    elif config.mode == CaptionMode.PRODUCT_LISTING:
        base = "Write a caption for this image as though it were a product listing"
    elif config.mode == CaptionMode.SOCIAL_MEDIA:
        base = "Write a caption for this image as if it were being used for a social media post"
    else:
        raise ValueError(f"Unknown caption mode: {config.mode}")
    # Add length constraints if specified
    if config.word_count:
        base += f" within {config.word_count} words"
    elif config.length:
        base += f". Keep it {config.length}"
    
    return base


def build_extra_instructions(config: PromptConfig) -> List[str]:
    """Build list of extra instructions based on config"""
    instructions = []
    
    if config.character_name:
        instructions.append(f"If there is a person/character in the image you must refer to them as {config.character_name}")
    
    if config.exclude_unchangeable_attributes:
        instructions.append("Do NOT include information about people/characters that cannot be changed (like ethnicity, gender, etc), but do still include changeable attributes (like hair style)")
    
    if config.include_lighting:
        instructions.append("Include information about lighting")
    
    if config.include_camera_angle:
        instructions.append("Include information about camera angle")
    
    if config.include_watermark_info:
        instructions.append("Include information about whether there is a watermark or not")
    
    if config.include_artifact_info:
        instructions.append("Include information about whether there are JPEG artifacts or not")
    
    if config.include_camera_details:
        instructions.append("If it is a photo you MUST include information about what camera was likely used and details such as aperture, shutter speed, ISO, etc")
    
    if config.keep_pg:
        instructions.append("Do NOT include anything sexual; keep it PG")
    
    if config.exclude_resolution:
        instructions.append("Do NOT mention the image's resolution")
    
    if config.include_quality_assessment:
        instructions.append("You MUST include information about the subjective aesthetic quality of the image from low to very high")
    
    if config.include_composition:
        instructions.append("Include information on the image's composition style, such as leading lines, rule of thirds, or symmetry")
    
    if config.exclude_text:
        instructions.append("Do NOT mention any text that is in the image")
    
    if config.include_depth_of_field:
        instructions.append("Specify the depth of field and whether the background is in focus or blurred")
    
    if config.include_lighting_source:
        instructions.append("If applicable, mention the likely use of artificial or natural lighting sources")
    
    if config.avoid_ambiguity:
        instructions.append("Do NOT use any ambiguous language")
    
    if config.include_sfw_rating:
        instructions.append("Include whether the image is sfw, suggestive, or nsfw")
    
    if config.only_important_elements:
        instructions.append("ONLY describe the most important elements of the image")
    
    return instructions


def build_prompt(config: Optional[PromptConfig] = None) -> Prompt:
    """Build a complete prompt with the given configuration"""
    if config is None:
        config = get_default_config()
    
    # Build base prompt
    prompt_parts = [build_base_prompt(config)]
    logger.info(f"Built base prompt: {prompt_parts[0]}")
    # Add extra instructions
    extra_instructions = build_extra_instructions(config)
    if extra_instructions:
        prompt_parts.extend(extra_instructions)
        logger.info(f"Built extra instructions: {extra_instructions}")
    # Join all parts with periods
    final_prompt = ". ".join(prompt_parts) + "."
    
    return Prompt(
        prompt_config=config,
        config_name=config.config_name,
        prompt=final_prompt,
        weight=1.0
    )


def build_prompts(configs: List[PromptConfig]) -> List[Prompt]:
    """Build a list of prompts from a list of configurations"""
    prompts = []
    for config in configs:
        prompt = build_prompt(config)
        logger.info(f"Built prompt for config {config.config_name}: {prompt.prompt}")
        prompts.append(prompt)
    return prompts

def get_default_config() -> PromptConfig:
    """Get the default prompt configuration"""
    return PromptConfig(
        config_name="descriptive",
        mode=CaptionMode.DESCRIPTIVE,
        tone=ToneStyle.FORMAL,
        exclude_resolution=True,
        avoid_ambiguity=True,
        exclude_text=True,
        only_important_elements=True,
        use_case="General Purpose",
        description="Default configuration for general image description with formal tone and essential elements only."
    )


def get_preset_configs() -> List[PromptConfig]:
    """Get a list of preset prompt configurations"""
    return [
        PromptConfig(
            config_name="descriptive_formal",
            mode=CaptionMode.DESCRIPTIVE,
            tone=ToneStyle.FORMAL,
            use_case="Content Description",
            description="Formal description focusing on key elements of the image. Ideal for accessibility, content indexing, and general documentation."
        ),
        PromptConfig(
            config_name="art_critic",
            mode=CaptionMode.ART_CRITIC,
            include_composition=True,
            include_lighting=True,
            include_quality_assessment=True,
            use_case="Art Analysis",
            description="Detailed artistic analysis including composition, lighting, and quality assessment. Suitable for art collections, galleries, and educational contexts."
        ),
        PromptConfig(
            config_name="technical_photo",
            mode=CaptionMode.DESCRIPTIVE,
            tone=ToneStyle.FORMAL,
            include_camera_details=True,
            include_lighting=True,
            include_depth_of_field=True,
            include_composition=True,
            use_case="Photography Technical Analysis",
            description="Technical analysis of photographic elements including camera settings, lighting, and composition. Useful for photography education and archival purposes."
        ),
        PromptConfig(
            config_name="social_media",
            mode=CaptionMode.SOCIAL_MEDIA,
            tone=ToneStyle.CASUAL,
            length="short",
            keep_pg=True,
            include_sfw_rating=True,
            use_case="Social Media Content",
            description="Engaging, casual descriptions suitable for social media posts. Includes content rating and maintains family-friendly content."
        ),
        PromptConfig(
            config_name="product_listing",
            mode=CaptionMode.PRODUCT_LISTING,
            tone=ToneStyle.FORMAL,
            include_quality_assessment=True,
            avoid_ambiguity=True,
            exclude_text=True,
            use_case="E-commerce",
            description="Product-focused descriptions highlighting key features and quality. Ideal for e-commerce listings and product catalogs."
        ),
        PromptConfig(
            config_name="training_data",
            mode=CaptionMode.TRAINING,
            include_lighting=True,
            include_composition=True,
            include_quality_assessment=True,
            exclude_text=True,
            use_case="AI Training Data",
            description="Detailed descriptions formatted for AI training purposes. Includes technical aspects while maintaining clean, consistent formatting."
        )
    ]


def list_available_configs() -> List[Dict[str, str]]:
    """List all available preset configurations with their use cases and descriptions"""
    configs = get_preset_configs()
    return [{
        'name': config.config_name,
        'mode': config.mode.value,
        'use_case': config.use_case or "Not specified",
        'description': config.description or "No description available"
    } for config in configs]
