# provider_manager.py


from loguru import logger

from .gemini_client import GeminiClient
from .ollama_client import OllamaClient
from .openai_client import OpenAIClient
from .provider_config import load_provider_config
from .vllm_client import VLLMClient

# from .ollama_client import OllamaClient  # for example, if you wrote an Ollama wrapper
# from .vlm_client import VLMClient        # for a hypothetical vLLM wrapper
# etc.


class ProviderManager:
    def __init__(self, config_path: str = "provider.config.toml"):
        logger.info(f"Initializing ProviderManager with config from {config_path}")
        self.config = load_provider_config(config_path)
        self._clients = {}
        # Initialize all clients at startup
        self._initialize_clients()

    def _initialize_clients(self):
        """
        Initialize all configured clients based on the TOML configuration.
        """
        logger.info("Initializing all configured clients")

        # Initialize cloud providers
        if "provider" in self.config:
            cloud_providers = self.config["provider"].get("cloud", {})
            for provider_name, provider_config in cloud_providers.items():
                try:
                    full_name = f"cloud.{provider_name}"
                    logger.debug(f"Attempting to initialize cloud provider '{full_name}'")
                    client = self.get_client(full_name)
                    self._clients[full_name] = client
                except ValueError as e:
                    logger.warning(f"Skipping cloud provider '{full_name}': {str(e)}")
                    continue

        # Initialize custom providers
        if "providers" in self.config and "custom" in self.config["providers"]:
            custom_providers = self.config["providers"]["custom"]
            for provider_name, provider_config in custom_providers.items():
                try:
                    full_name = f"custom.{provider_name}"
                    logger.debug(f"Attempting to initialize custom provider '{full_name}'")
                    client = self.get_client(full_name)
                    self._clients[full_name] = client
                except ValueError as e:
                    logger.warning(f"Skipping custom provider '{full_name}': {str(e)}")
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
        provider_config = self._get_provider_config(provider_name)
        if not provider_config:
            logger.error(f"No config found for provider '{provider_name}'")
            raise ValueError(f"No config found for provider '{provider_name}'")

        base_url = provider_config.get("base_url", "https://api.openai.com/v1")
        api_key = provider_config.get("api_key")
        logger.debug(f"Using base_url: {base_url} for provider '{provider_name}'")

        try:
            if provider_name == "cloud.openai":
                client = OpenAIClient(api_key=api_key, base_url=base_url)
            elif provider_name == "custom.ollama":
                client = OllamaClient(api_key=api_key, base_url=base_url)
            elif provider_name == "custom.vllm-pixtral":
                client = VLLMClient(api_key=api_key, base_url=base_url)
            elif provider_name == "cloud.gemini":
                client = GeminiClient(api_key=api_key, base_url=base_url)
            else:
                logger.error(f"Unknown provider or not implemented: {provider_name}")
                raise ValueError(f"Unknown provider or not implemented: {provider_name}")

            logger.info(f"Successfully created client for provider '{provider_name}'")
            self._clients[provider_name] = client
            return client

        except Exception as e:
            logger.error(f"Failed to create client for provider '{provider_name}': {str(e)}")
            raise
