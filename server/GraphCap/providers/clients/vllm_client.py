from typing import Any, Dict, List, Type, Union

import httpx
from loguru import logger
from pydantic import BaseModel

from .base_client import BaseClient


class VLLMClient(BaseClient):
    """Client for VLLM API with OpenAI compatibility layer"""

    def __init__(self, name: str, kind: str, environment: str, env_var: str, base_url: str, default_model: str):
        # If base_url doesn't include /v1, append it
        if not base_url.endswith("/v1"):
            base_url = f"{base_url}/v1"

        logger.info(f"VLLMClient initialized with base_url: {base_url}")
        super().__init__(
            name=name,
            kind=kind,
            environment=environment,
            env_var=env_var,
            base_url=base_url.rstrip("/"),
            default_model=default_model,
        )

    def _format_vision_content(self, text: str, image_data: str) -> List[Dict]:
        """Format vision content for VLLM API"""
        return [
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},
        ]

    def create_structured_completion(
        self, messages: List[Dict], schema: Union[Dict, Type[BaseModel], BaseModel], model: str, **kwargs
    ) -> Any:
        """Create a chat completion with structured output following a JSON schema."""
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

    async def health(self):
        """Check the health of the VLLM API"""
        base_url = str(self.base_url).replace("/v1/", "")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{base_url}/health")
                logger.debug(f"VLLM health check status: {response.status_code}")

                # Try to parse JSON response if available
                try:
                    response_data = response.json()
                    logger.debug(f"VLLM health check response: {response_data}")
                except Exception as e:
                    logger.debug(f"VLLM health check response was not JSON: {str(e)}")

                # Consider it healthy if we get a 200 status code
                return response.status_code == 200

            except Exception as e:
                logger.error(f"VLLM health check failed: {str(e)}")
                return False
