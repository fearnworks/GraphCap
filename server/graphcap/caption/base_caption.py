"""
# SPDX-License-Identifier: Apache-2.0
Base Caption Module

Provides base classes and shared functionality for different caption types.
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ..providers.clients.base_client import BaseClient
from ..schemas.structured_vision import StructuredVisionConfig


class BaseCaptionProcessor:
    """
    Base class for caption processors.

    Provides shared functionality for processing images with vision models
    and handling responses. Subclasses implement specific caption formats.

    Attributes:
        config_name (str): Name of this caption processor
        version (str): Version of the processor
        prompt (str): Instruction prompt for the vision model
        schema (BaseModel): Pydantic model for response validation
    """

    def __init__(
        self,
        config_name: str,
        version: str,
        prompt: str,
        schema: type[BaseModel],
    ):
        self.vision_config = StructuredVisionConfig(
            config_name=config_name,
            version=version,
            prompt=prompt,
            schema=schema,
        )

    async def process_single(
        self,
        provider: BaseClient,
        image_path: Path,
        max_tokens: Optional[int] = 2048,
        temperature: Optional[float] = 0.8,
        top_p: Optional[float] = 0.9,
    ) -> dict:
        """
        Process a single image and return caption data.

        Args:
            provider: Vision AI provider client instance
            image_path: Path to the image file
            max_tokens: Maximum tokens for model response
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter

        Returns:
            dict: Structured caption data according to schema

        Raises:
            Exception: If image processing fails
        """
        try:
            completion = await provider.vision(
                prompt=self.vision_config.prompt,
                image=image_path,
                schema=self.vision_config.schema,
                model=provider.default_model,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
            )

            # Handle response parsing
            if isinstance(completion, BaseModel):
                result = completion.choices[0].message.parsed
                if isinstance(result, BaseModel):
                    result = result.model_dump()
            else:
                result = completion.choices[0].message.parsed
                if "choices" in result:
                    result = result["choices"][0]["message"]["parsed"]["parsed"]
                elif "message" in result:
                    result = result["message"]["parsed"]

            return result
        except Exception as e:
            raise Exception(f"Error processing {image_path}: {str(e)}")

    async def process_batch(
        self,
        provider: BaseClient,
        image_paths: List[Path],
        max_tokens: Optional[int] = 1024,
        temperature: Optional[float] = 0.8,
        top_p: Optional[float] = 0.9,
    ) -> List[Dict[str, Any]]:
        """
        Process multiple images and return their captions.

        Args:
            provider: Vision AI provider client instance
            image_paths: List of paths to image files
            max_tokens: Maximum tokens for model response
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter

        Returns:
            List[Dict[str, Any]]: List of caption results with metadata
        """
        tasks = [
            self.process_single(
                provider=provider,
                image_path=path,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
            )
            for path in image_paths
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [
            {
                "filename": f"./{Path(str(path)).name}",
                "config_name": self.vision_config.config_name,
                "version": self.vision_config.version,
                "model": provider.default_model,
                "provider": provider.name,
                "parsed": result if not isinstance(result, Exception) else {"error": str(result)},
            }
            for path, result in zip(image_paths, results)
        ]
