from typing import Any, Dict, List, Optional, Type, Union

from loguru import logger
from pydantic import BaseModel

from .base_client import BaseClient


class VLLMClient(BaseClient):
    """Client for VLLM API with OpenAI compatibility layer"""

    def __init__(self, api_key: Optional[str], base_url: str):
        # Ensure base_url doesn't end with a slash
        base_url = base_url.rstrip("/")

        # If base_url doesn't include /v1, append it
        if not base_url.endswith("/v1"):
            base_url = f"{base_url}/v1"

        logger.info(f"VLLMClient initialized with base_url: {base_url}")
        super().__init__(api_key=api_key or "EMPTY", base_url=base_url)

    def _format_vision_content(self, text: str, image_data: str) -> List[Dict]:
        """Format vision content for VLLM API"""
        return [
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},
        ]

    def create_structured_completion(
        self, messages: List[Dict], schema: Union[Dict, Type[BaseModel], BaseModel], model: str, **kwargs
    ) -> Any:
        """
        Create a chat completion with structured output following a JSON schema.

        Args:
            messages: List of message dictionaries
            schema: JSON Schema dict or Pydantic model class/instance
            model: Model ID (must support structured outputs)
            **kwargs: Additional arguments to pass to create()

        Returns:
            If schema is a Pydantic model, returns an instance of that model
            Otherwise returns the raw completion
        """
        json_schema = self._get_schema_from_input(schema)

        try:
            logger.debug(f"Creating structured completion with model: {model}")
            completion = self.chat.completions.create(
                model=model, messages=messages, extra_body={"guided_json": json_schema}, **kwargs
            )

            # If schema is a Pydantic model, parse the response
            if isinstance(schema, type) and issubclass(schema, BaseModel):
                return schema.model_validate_json(completion.choices[0].message.content)
            elif isinstance(schema, BaseModel):
                return schema.__class__.model_validate_json(completion.choices[0].message.content)
            return completion

        except Exception as e:
            logger.error(f"Failed to create structured completion: {str(e)}")
            raise
