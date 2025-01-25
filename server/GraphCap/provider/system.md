# Provider Management System

A flexible provider management system for handling multiple AI service providers with an OpenAI-compatible interface.

## Overview

This system provides a unified way to manage and interact with different AI providers, both cloud-based and custom implementations. It uses a TOML-based configuration system and provides OpenAI-compatible client interfaces for each provider.

## Configuration

### Provider Config File (provider.config.toml)

The system is configured using a TOML file that defines both cloud and custom providers:

```toml
[provider.cloud.openai]
api_key = "OPENAI_API_KEY"
base_url = "https://api.openai.com/v1"
models = ["gpt-4-vision", "gpt-4"]

[providers.custom.ollama]
api_key = "CUSTOM_KEY"
base_url = "http://localhost:11434"
fetch_models = true
```

### Provider Types

1. Cloud Providers (`provider.cloud.*`)
   - OpenAI
   - Gemini
   - OpenRouter (commented example)

2. Custom Providers (`providers.custom.*`)
   - Ollama
   - VLLM
   - Other custom implementations

## Usage

### Basic Usage

```python
from provider.providers.provider_manager import ProviderManager

# Initialize the manager
manager = ProviderManager("provider.config.toml")

# Get all initialized clients
clients = manager.clients()

# Get a specific client
openai_client = manager.get_client("cloud.openai")
ollama_client = manager.get_client("custom.ollama")
```

### Provider Clients

All provider clients implement an OpenAI-compatible interface:

- `OpenAI`: Standard OpenAI client
- `OllamaClient`: Ollama-specific implementation
- `VLLMClient`: VLLM-specific implementation
- `GeminiClient`: Google Gemini implementation

## Features

- **Unified Interface**: All providers use an OpenAI-compatible interface
- **Configuration Management**: TOML-based configuration for easy customization
- **Automatic Initialization**: Providers are initialized at startup
- **Error Handling**: Robust error handling with detailed logging
- **Caching**: Clients are cached after initialization
- **Extensible**: Easy to add new provider implementations

## Logging

The system uses loguru for comprehensive logging:

- DEBUG: Detailed debugging information
- INFO: General operational information
- WARNING: Handled issues that don't prevent operation
- ERROR: Serious issues that prevent proper operation

## Adding New Providers

1. Create a new provider client class that inherits from `OpenAI`
2. Add the provider configuration to `provider.config.toml`
3. Update the `get_client` method in `ProviderManager` to handle the new provider

Example:
```python
class NewProvider(OpenAI):
    def __init__(self, api_key: str, base_url: str):
        super().__init__(api_key=api_key, base_url=base_url)
```

## Error Handling

The system includes comprehensive error handling:
- Configuration validation
- Client initialization errors
- Runtime errors with detailed logging

## Dependencies

- `openai`: Base client implementation
- `loguru`: Logging system
- `tomllib`: TOML configuration parsing
- Provider-specific dependencies as needed

## Best Practices

1. Always use environment variables for API keys
2. Keep the configuration file secure
3. Monitor logs for initialization and runtime issues
4. Handle provider-specific rate limits and quotas
5. Implement proper error handling in your application

## Contributing

1. Follow the existing code structure
2. Add comprehensive logging
3. Implement proper error handling
4. Add tests for new functionality
5. Update documentation as needed