from typing import Dict, List

from loguru import logger

from .base_client import BaseClient


class OpenRouterClient(BaseClient):
    """Client for OpenRouter API with OpenAI compatibility layer"""

    def __init__(self, name: str, kind: str, environment: str, env_var: str, base_url: str, default_model: str):
        logger.info(f"OpenRouterClient initialized with base_url: {base_url}")
        super().__init__(
            name=name,
            kind=kind,
            environment=environment,
            env_var=env_var,
            base_url=base_url.rstrip("/"),
            default_model=default_model,
        )

    def _format_vision_content(self, text: str, image_data: str) -> List[Dict]:
        """Format vision content for OpenRouter API"""
        return [
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}},
        ]

    async def _prepare_request(self, request, *args, **kwargs):
        """Hook for modifying requests before they're sent"""
        # Add OpenRouter-specific headers if provided
        headers = {}
        if hasattr(self, "app_url"):
            headers["HTTP-Referer"] = self.app_url
        if hasattr(self, "app_title"):
            headers["X-Title"] = self.app_title

        # Add headers directly to the request object
        request.headers.update(headers)
        logger.debug(f"Preparing request with headers: {headers}")

        # Call parent without extra_headers
        return await super()._prepare_request(request, *args, **kwargs)

    async def get_available_models(self):
        """Get list of available models from OpenRouter."""
        try:
            models = await self.models.list()
            logger.debug(f"Retrieved {len(models.data)} models from OpenRouter")
            return models
        except Exception as e:
            logger.error(f"Failed to get models from OpenRouter: {str(e)}")
            raise

    def create_structured_completion(self, messages: List[Dict], schema: Dict, model: str = "openai/gpt-4", **kwargs):
        """
        Create a chat completion with structured output following a JSON schema.

        Args:
            messages: List of message dictionaries
            schema: JSON Schema object defining the expected response format
            model: Model ID (must support structured outputs)
            **kwargs: Additional arguments to pass to create()
        """
        try:
            logger.debug(f"Creating structured completion with model: {model}")
            return self.chat.completions.create(
                model=model,
                messages=messages,
                response_format={
                    "type": "json_schema",
                    "json_schema": {"name": schema.get("name", "response"), "strict": True, "schema": schema},
                },
                **kwargs,
            )
        except Exception as e:
            logger.error(f"Failed to create structured completion: {str(e)}")
            raise

    def create_chat_completion(
        self, messages: List[Dict], model: str = "google/gemini-2.0-flash-exp:free", stream: bool = False, **kwargs
    ):
        """
        Convenience method for creating chat completions with OpenRouter.

        Args:
            messages: List of message dictionaries
            model: Model ID (default: gpt-3.5-turbo)
            stream: Whether to stream the response
            **kwargs: Additional arguments to pass to create()
        """
        try:
            logger.debug(f"Creating chat completion with model: {model}")
            return self.chat.completions.create(model=model, messages=messages, stream=stream, **kwargs)
        except Exception as e:
            logger.error(f"Failed to create chat completion: {str(e)}")
            raise
