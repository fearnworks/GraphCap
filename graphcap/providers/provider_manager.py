# provider_manager.py

"""
# SPDX-License-Identifier: Apache-2.0
graphcap.providers.provider_manager

Manages provider clients with configuration from files or environment variables.

Key features:
- Environment variable fallback
- Multiple provider support
- Client caching
- Configuration validation
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger

from .clients import GeminiClient, OllamaClient, OpenAIClient, OpenRouterClient, VLLMClient
from .provider_config import ProviderConfig, get_providers_config


class ProviderManager:
    """
    Manages provider clients with configuration from files or environment.

    Falls back to environment variables if no config file is found.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize provider manager.

        Args:
            config_path: Optional path to provider config file
        """
        self._clients = {}
        self.providers: Dict[str, ProviderConfig] = {}

        # Try config file first
        if config_path:
            try:
                logger.info(f"Loading provider config from {config_path}")
                self.providers = get_providers_config(config_path)
            except FileNotFoundError:
                logger.warning(f"Config file not found: {config_path}, falling back to environment")
                self._load_from_environment()
        else:
            # Try default config path from environment
            default_config = os.getenv("DEFAULT_PROVIDER_CONFIG")
            if default_config and Path(default_config).exists():
                logger.info(f"Loading provider config from default path: {default_config}")
                self.providers = get_providers_config(default_config)
            else:
                logger.info("No config file found, using environment variables")
                self._load_from_environment()

    def _load_from_environment(self):
        """Load provider configurations from environment variables."""
        # OpenAI
        if os.getenv("OPENAI_API_KEY"):
            self.providers["openai"] = ProviderConfig(
                kind="openai",
                environment="cloud",
                env_var="OPENAI_API_KEY",
                base_url="https://api.openai.com/v1",
                models=["gpt-4-vision-preview"],
                default_model="gpt-4-vision-preview",
            )

        # Gemini
        if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
            self.providers["gemini"] = ProviderConfig(
                kind="gemini",
                environment="cloud",
                env_var="GEMINI_API_KEY" if os.getenv("GEMINI_API_KEY") else "GOOGLE_API_KEY",
                base_url="https://generativelanguage.googleapis.com/v1beta",
                models=["gemini-2.0-flash-exp"],
                default_model="gemini-2.0-flash-exp",
            )

        # VLLM
        if os.getenv("VLLM_BASE_URL"):
            self.providers["vllm"] = ProviderConfig(
                kind="vllm",
                environment="local",
                env_var="NONE",
                base_url=os.getenv("VLLM_BASE_URL", "http://localhost:11435"),
                models=["vision-worker"],
                default_model="vision-worker",
            )

        # Ollama
        if os.getenv("OLLAMA_BASE_URL"):
            self.providers["ollama"] = ProviderConfig(
                kind="ollama",
                environment="local",
                env_var="NONE",
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                models=[],
                default_model="llama3.2",
                fetch_models=True,
            )

        if not self.providers:
            logger.warning("No provider configurations found in environment")

    def clients(self) -> Dict[str, Any]:
        """Get all initialized clients."""
        return self._clients

    def get_client(self, provider_name: str):
        """Get or create a client for the specified provider."""
        if provider_name in self._clients:
            return self._clients[provider_name]

        if provider_name not in self.providers:
            raise ValueError(f"No configuration found for provider: {provider_name}")

        config = self.providers[provider_name]
        client_args = {
            "name": provider_name,
            "kind": config.kind,
            "environment": config.environment,
            "env_var": config.env_var,
            "base_url": config.base_url,
            "default_model": config.default_model,
        }

        try:
            client = None
            if config.kind == "openai":
                client = OpenAIClient(**client_args)
            elif config.kind == "gemini":
                client = GeminiClient(**client_args)
            elif config.kind == "vllm":
                client = VLLMClient(**client_args)
            elif config.kind == "ollama":
                client = OllamaClient(**client_args)
            elif config.kind == "openrouter":
                client = OpenRouterClient(**client_args)
            else:
                raise ValueError(f"Unknown provider kind: {config.kind}")

            if config.rate_limits:
                client.requests_per_minute = config.rate_limits.requests_per_minute
                client.tokens_per_minute = config.rate_limits.tokens_per_minute

            self._clients[provider_name] = client
            return client

        except Exception as e:
            logger.error(f"Failed to create client for {provider_name}: {str(e)}")
            raise
