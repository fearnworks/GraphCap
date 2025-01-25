from pathlib import Path
from typing import Dict, List, Union

from loguru import logger
from openai import OpenAI


class OpenRouterClient(OpenAI):
    name = "openrouter"
    default_model = "openai/gpt-4o-mini"

    def __init__(
        self, api_key: str, base_url: str = "https://openrouter.ai/api/v1", app_url: str = None, app_title: str = None
    ):
        # Ensure base_url doesn't end with a slash
        base_url = base_url.rstrip("/")
        logger.info(f"OpenRouterClient initialized with base_url: {base_url}")

        self.app_url = app_url
        self.app_title = app_title
        super().__init__(api_key=api_key, base_url=base_url)

    def _prepare_request(self, request, *args, **kwargs):
        """Hook for modifying requests before they're sent"""
        # Add OpenRouter-specific headers if provided
        headers = {}
        if self.app_url:
            headers["HTTP-Referer"] = self.app_url
        if self.app_title:
            headers["X-Title"] = self.app_title

        # Add headers directly to the request object
        request.headers.update(headers)
        logger.debug(f"Preparing request with headers: {headers}")

        # Call parent without extra_headers
        return super()._prepare_request(request, *args, **kwargs)

    def _format_vision_content(self, text: str, image_data: str) -> List[Dict]:
        """Format vision content for OpenRouter API"""
        return [
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}},
        ]

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

    def vision(self, prompt: str, image: Union[str, Path], model: str = "openai/gpt-4o-mini"):
        """
        Create a vision completion with the given prompt and image.

        Args:
            prompt: Text prompt to send with the image
            image: Path to image file or base64 encoded image string
            model: Model to use for completion (must support vision)
            max_tokens: Maximum tokens in response
        """
        return super().vision(prompt=prompt, image=image, model=model)

    def get_available_models(self):
        """
        Get list of available models from OpenRouter.
        Example models:
        - anthropic/claude-2
        - openai/gpt-4
        - google/gemini-2.0-flash-exp
        - meta-llama/llama-3.2-90b-vision-instruct:free
        """
        try:
            models = self.models.list()
            logger.debug(f"Retrieved {len(models.data)} models from OpenRouter")
            return models
        except Exception as e:
            logger.error(f"Failed to get models from OpenRouter: {str(e)}")
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
