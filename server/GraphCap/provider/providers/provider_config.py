import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class ProviderConfig:
    """Configuration for a single provider"""

    api_key: str
    base_url: str
    models: List[str]
    fetch_models: bool = False


@dataclass
class ProvidersConfig:
    """Root configuration containing all providers"""

    cloud: Dict[str, ProviderConfig]
    custom: Dict[str, ProviderConfig]


def load_provider_config(config_path: str | Path = "provider.config.toml") -> Dict[str, Any]:
    """
    Load provider configuration from a TOML file.

    Args:
        config_path: Path to the TOML configuration file

    Returns:
        Dict containing the parsed configuration

    Raises:
        FileNotFoundError: If config file doesn't exist
        tomllib.TOMLDecodeError: If config file is invalid TOML
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    # Open the file in binary mode for tomllib
    with config_path.open("rb") as f:
        return tomllib.load(f)


def parse_provider_config(config_data: Dict[str, Any]) -> ProviderConfig:
    """Parse a single provider's configuration data into a ProviderConfig object"""
    return ProviderConfig(
        api_key=os.getenv(config_data["api_key"]) or config_data["api_key"],
        base_url=config_data["base_url"],
        models=config_data.get("models", []),
        fetch_models=config_data.get("fetch_models", False),
    )


def get_providers_config(config_path: str | Path = "provider.config.toml") -> ProvidersConfig:
    """
    Load and parse the full providers configuration.

    Args:
        config_path: Path to the TOML configuration file

    Returns:
        ProvidersConfig object containing all provider configurations

    Example config:
        [provider.cloud.openai]
        api_key = "OPENAI_API_KEY"
        base_url = "https://api.openai.com/v1"
        models = ["gpt-4", "gpt-3.5-turbo"]

        [providers.custom.ollama]
        api_key = "CUSTOM_KEY"
        base_url = "http://localhost:11434"
        fetch_models = true
    """
    config = load_provider_config(config_path)

    # Parse cloud providers
    cloud_providers = {}
    cloud_config = config.get("provider", {}).get("cloud", {})
    for name, provider_config in cloud_config.items():
        cloud_providers[name] = parse_provider_config(provider_config)

    # Parse custom providers
    custom_providers = {}
    custom_config = config.get("providers", {}).get("custom", {})
    for name, provider_config in custom_config.items():
        custom_providers[name] = parse_provider_config(provider_config)

    return ProvidersConfig(cloud=cloud_providers, custom=custom_providers)


def validate_config(config: ProvidersConfig) -> List[str]:
    """
    Validate the provider configuration.

    Args:
        config: ProvidersConfig object to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Validate all providers
    for provider_type, providers in [("cloud", config.cloud), ("custom", config.custom)]:
        for name, provider in providers.items():
            # Required fields
            if not provider.api_key:
                errors.append(f"{provider_type}.{name}: Missing API key")
            if not provider.base_url:
                errors.append(f"{provider_type}.{name}: Missing base URL")

            # URL format
            if provider.base_url and not (
                provider.base_url.startswith("http://") or provider.base_url.startswith("https://")
            ):
                errors.append(f"{provider_type}.{name}: Base URL must start with http:// or https://")

            # Models list when fetch_models is False
            if not provider.fetch_models and not provider.models:
                errors.append(f"{provider_type}.{name}: Must specify models list when fetch_models is False")

    return errors


if __name__ == "__main__":
    # Example usage
    try:
        config = get_providers_config()
        errors = validate_config(config)

        if errors:
            print("Configuration errors found:")
            for error in errors:
                print(f"- {error}")
        else:
            print("Configuration loaded successfully:")
            print("\nCloud Providers:")
            for name, provider in config.cloud.items():
                print(f"- {name}:")
                print(f"  Base URL: {provider.base_url}")
                print(f"  Models: {', '.join(provider.models) if provider.models else '[fetch at runtime]'}")

            print("\nCustom Providers:")
            for name, provider in config.custom.items():
                print(f"- {name}:")
                print(f"  Base URL: {provider.base_url}")
                print(f"  Models: {', '.join(provider.models) if provider.models else '[fetch at runtime]'}")

    except Exception as e:
        print(f"Error loading configuration: {e}")
