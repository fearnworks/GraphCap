from loguru import logger
from openai import OpenAI


class OllamaClient(OpenAI):
    def __init__(self, api_key: str, base_url: str):
        self.base_url = base_url
        super().__init__(api_key=api_key, base_url=base_url)
        logger.info(f"OllamaClient initialized with base_url: {base_url}")

    def models(self):
        return self.get("models")
