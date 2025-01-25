import base64
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Type, Union

from loguru import logger
from openai import OpenAI
from pydantic import BaseModel


class BaseClient(OpenAI, ABC):
    """Abstract base class for all provider clients"""

    def __init__(self, api_key: str, base_url: str):
        super().__init__(api_key=api_key, base_url=base_url)

    @abstractmethod
    def _format_vision_content(self, text: str, image_data: str) -> List[Dict]:
        """Format the vision content according to provider specifications"""
        pass

    def _get_schema_from_input(self, schema: Union[Dict, Type[BaseModel], BaseModel]) -> Dict:
        """Convert input schema to JSON Schema dict"""
        if isinstance(schema, dict):
            return schema
        elif isinstance(schema, type) and issubclass(schema, BaseModel):
            return schema.model_json_schema()
        elif isinstance(schema, BaseModel):
            return schema.__class__.model_json_schema()
        else:
            raise ValueError("Schema must be either a dict or a Pydantic model/instance")

    def _get_base64_image(self, image_path: Union[str, Path]) -> str:
        """Helper method to convert image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def vision(self, prompt: str, image: Union[str, Path], model: str, max_tokens: int = 100, **kwargs):
        """Create a vision completion"""
        # Handle image input
        if isinstance(image, (str, Path)) and not str(image).startswith("data:"):
            image_data = self._get_base64_image(image)
        else:
            image_data = image.split("base64,")[1] if "base64," in image else image

        # Get provider-specific message format
        content = self._format_vision_content(prompt, image_data)

        try:
            completion = self.chat.completions.create(
                model=model, messages=[{"role": "user", "content": content}], max_tokens=max_tokens, **kwargs
            )
            return completion
        except Exception as e:
            logger.error(f"Vision completion failed: {str(e)}")
            raise
