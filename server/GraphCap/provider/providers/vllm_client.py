from loguru import logger
from openai import OpenAI


class VLLMClient(OpenAI):
    def __init__(self, api_key: str, base_url: str):
        # Ensure base_url doesn't end with a slash
        base_url = base_url.rstrip("/")

        # If base_url doesn't include /v1, append it
        if not base_url.endswith("/v1"):
            base_url = f"{base_url}/v1"

        logger.info(f"VLLMClient initialized with base_url: {base_url}")
        super().__init__(api_key=api_key, base_url=base_url)

    def _prepare_request(self, *args, **kwargs):
        """Hook for modifying requests before they're sent"""
        # Add any VLLM-specific request modifications here if needed
        return super()._prepare_request(*args, **kwargs)
