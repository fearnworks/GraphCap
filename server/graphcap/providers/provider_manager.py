# provider_manager.py


from loguru import logger

from .clients import GeminiClient, OllamaClient, OpenAIClient, OpenRouterClient, VLLMClient
from .provider_config import get_providers_config


class ProviderManager:
    def __init__(self, config_path: str = "provider.config.toml"):
        logger.info(f"Initializing ProviderManager with config from {config_path}")
        self.providers = get_providers_config(config_path)
        self._clients = {}
        # Initialize all clients at startup
        self._initialize_clients()

    def _initialize_clients(self):
        """
        Initialize all configured clients based on the TOML configuration.
        """
        logger.info("Initializing all configured clients")

        for name, config in self.providers.items():
            try:
                logger.debug(f"Attempting to initialize provider '{name}'")
                client = self.get_client(name)
                self._clients[name] = client
            except ValueError as e:
                logger.warning(f"Skipping provider '{name}': {str(e)}")
                continue

        logger.info(f"Successfully initialized {len(self._clients)} clients")

    def clients(self):
        """
        Returns a dictionary of all initialized provider clients.
        """
        return self._clients

    def _get_provider_config(self, provider_name: str):
        logger.debug(f"Getting config for provider '{provider_name}'")
        category, name = provider_name.split(".")

        if category == "cloud":
            if "provider" in self.config and "cloud" in self.config["provider"]:
                cloud_config = self.config["provider"]["cloud"]
                if name in cloud_config:
                    logger.debug(f"Found cloud config for provider '{provider_name}'")
                    return cloud_config[name]
        elif category == "custom":
            if "providers" in self.config and "custom" in self.config["providers"]:
                custom_config = self.config["providers"]["custom"]
                if name in custom_config:
                    logger.debug(f"Found custom config for provider '{provider_name}'")
                    return custom_config[name]

        logger.debug(f"No config found for provider '{provider_name}'")
        return None

    def get_client(self, provider_name: str):
        """
        Returns an OpenAI-compatible client for the given provider name.
        Caches and reuses the client if called repeatedly.
        """
        if provider_name in self._clients:
            logger.debug(f"Returning cached client for provider '{provider_name}'")
            return self._clients[provider_name]

        logger.info(f"Creating new client for provider '{provider_name}'")

        if provider_name not in self.providers:
            logger.error(f"No config found for provider '{provider_name}'")
            raise ValueError(f"No config found for provider '{provider_name}'")

        config = self.providers[provider_name]
        try:
            client = None
            client_args = {
                "name": provider_name,
                "kind": config.kind,
                "environment": config.environment,
                "env_var": config.env_var,
                "base_url": config.base_url,
                "default_model": config.default_model,
            }

            if config.kind == "openai":
                client = OpenAIClient(**client_args)
            elif config.kind == "ollama":
                client = OllamaClient(**client_args)
            elif config.kind == "vllm":
                client = VLLMClient(**client_args)
            elif config.kind == "gemini":
                client = GeminiClient(**client_args)
            elif config.kind == "openrouter":
                client = OpenRouterClient(**client_args)
            else:
                logger.error(f"Unknown provider kind: {config.kind}")
                raise ValueError(f"Unknown provider kind: {config.kind}")

            logger.info(f"Successfully created client for provider '{provider_name}'")
            self._clients[provider_name] = client
            return client

        except Exception as e:
            logger.error(f"Failed to create client for provider '{provider_name}': {str(e)}")
            raise
