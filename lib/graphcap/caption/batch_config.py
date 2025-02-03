"""
# SPDX-License-Identifier: Apache-2.0
Batch Configuration Module

Provides functionality for parsing and validating batch processing configurations.
Handles image sampling and configuration validation.

Key features:
- Configuration parsing and validation
- Image sampling methods
- Parameter validation
"""

import random
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger
from pydantic import BaseModel, Field, field_validator


class SampleMethod(str, Enum):
    """Sampling methods for image selection."""

    RANDOM = "random"
    INCREMENTAL = "incremental"
    LATEST = "latest"


class InputConfig(BaseModel):
    """Input configuration settings."""

    path: Path = Field(..., description="Path to input directory or single image file")
    sample_size: int = Field(0, description="Number of images to sample (0 means use all)")
    sample_method: SampleMethod = Field(SampleMethod.RANDOM, description="Method to use when sampling images")


class ProviderConfig(BaseModel):
    """Provider configuration settings."""

    name: str = Field(..., description="Name of the AI provider to use")
    config_file: Path = Field(..., description="Path to provider configuration file")
    max_concurrent: int = Field(3, description="Maximum number of concurrent requests")

    @field_validator("max_concurrent")
    def validate_max_concurrent(cls, v):
        if v <= 0:
            raise ValueError("max_concurrent must be a positive integer")
        return v


class CaptionConfig(BaseModel):
    """Caption generation settings."""

    type: str = Field(..., description="Type of caption to generate")
    max_tokens: int = Field(4096, description="Maximum tokens to generate")
    temperature: float = Field(0.8, description="Sampling temperature")
    top_p: float = Field(0.9, description="Nucleus sampling threshold")
    repetition_penalty: float = Field(1.15, description="Repetition penalty")

    @field_validator("type")
    def validate_type(cls, v):
        if v not in ["graph", "art"]:
            raise ValueError('type must be either "graph" or "art"')
        return v

    @field_validator("max_tokens")
    def validate_max_tokens(cls, v):
        if v <= 0:
            raise ValueError("max_tokens must be a positive integer")
        return v

    @field_validator("temperature", "top_p")
    def validate_probability(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("value must be between 0 and 1")
        return v

    @field_validator("repetition_penalty")
    def validate_repetition_penalty(cls, v):
        if not 0 <= v <= 2:
            raise ValueError("repetition_penalty must be between 0 and 2")
        return v


class OutputConfig(BaseModel):
    """Output configuration settings."""

    directory: Optional[Path] = Field(None, description="Base directory for batch job outputs")
    store_logs: bool = Field(False, description="Store logs in the output directory")
    formats: List[str] = Field(default_factory=list, description="Additional output formats supported by the processor")
    copy_images: bool = Field(False, description="Copy images to output directory")


class BatchConfig(BaseModel):
    """Complete batch processing configuration."""

    input: InputConfig
    provider: ProviderConfig
    caption: CaptionConfig
    output: OutputConfig


def sample_images(
    image_paths: List[Path],
    sample_size: Optional[int] = None,
    method: Optional[SampleMethod] = None,
) -> List[Path]:
    """
    Sample a subset of images from the provided paths.

    Args:
        image_paths: List of image paths to sample from
        sample_size: Number of images to sample (None or 0 means use all)
        method: Sampling method (random, incremental, latest)

    Returns:
        List of sampled image paths
    """
    if not sample_size or sample_size <= 0 or sample_size >= len(image_paths):
        return image_paths

    method = method or SampleMethod.RANDOM
    sample_size = min(sample_size, len(image_paths))

    if method == SampleMethod.RANDOM:
        return random.sample(image_paths, sample_size)
    elif method == SampleMethod.INCREMENTAL:
        return image_paths[:sample_size]
    elif method == SampleMethod.LATEST:
        # Sort by modification time, newest first
        sorted_paths = sorted(image_paths, key=lambda p: p.stat().st_mtime, reverse=True)
        return sorted_paths[:sample_size]
    else:
        logger.warning(f"Unknown sampling method '{method}', using random sampling")
        return random.sample(image_paths, sample_size)


def get_image_paths(input_config: InputConfig) -> Tuple[List[Path], Dict[str, Any]]:
    """
    Get list of image paths based on input configuration.

    Args:
        input_config: Input configuration settings

    Returns:
        Tuple of (image_paths, sampling_info)
    """
    image_paths = []
    input_path = input_config.path

    if input_path.is_dir():
        # Supported image extensions
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        for ext in image_extensions:
            image_paths.extend(input_path.glob(f"**/*{ext}"))
    else:
        image_paths = [input_path]

    if not image_paths:
        raise ValueError("No image files found")

    original_count = len(image_paths)

    # Sample images if requested
    if input_config.sample_size > 0:
        image_paths = sample_images(
            image_paths,
            input_config.sample_size,
            input_config.sample_method,
        )
        logger.info(
            f"Sampled {len(image_paths)} images from {original_count} using {input_config.sample_method} method"
        )
    else:
        logger.info(f"Processing all {len(image_paths)} images")

    sampling_info = {
        "original_count": original_count,
        "sample_size": len(image_paths),
        "sample_method": input_config.sample_method if input_config.sample_size > 0 else "all",
    }

    return image_paths, sampling_info


def load_batch_config(config_file: Path) -> BatchConfig:
    """
    Load and validate batch configuration from file.

    Args:
        config_file: Path to TOML configuration file

    Returns:
        Validated BatchConfig object

    Raises:
        ValueError: If configuration is invalid
    """
    import tomllib

    try:
        with open(config_file, "rb") as f:
            config_data = tomllib.load(f)
        return BatchConfig(**config_data)
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"Failed to parse TOML configuration: {e}")
    except Exception as e:
        raise ValueError(f"Invalid configuration: {e}")
