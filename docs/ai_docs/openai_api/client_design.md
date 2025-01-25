# OpenAI Provider Client Design

## 1. Core Requirements
- Create provider clients that are 100% compatible with OpenAI's Python client interface
- Support multiple providers (OpenAI, Ollama, vLLM) through a unified interface
- Allow configuration via TOML file
- Fetch and filter available models from each provider

## 2. Provider Configuration (TOML)
```toml
[provider.cloud.openai]
api_key = "OPENAI_API_KEY"
base_url = "https://api.openai.com/v1"
models = ["gpt-4", "gpt-3.5-turbo"]

[providers.custom.ollama]
api_key = "CUSTOM_KEY"
base_url = "http://localhost:11434"
fetch_models = true
```

## 3. Client Interface
Each provider client must:
- Inherit from OpenAI base client
- Support all standard OpenAI resources (models, chat, completions, etc.)
- Be usable as a drop-in replacement for OpenAI client

```python
# Usage should be identical to OpenAI client
client = manager.get_client("provider_name")
models = client.models.list()
```

## 4. Model Listing
- Support both static model lists and runtime fetching
- Convert provider-specific model formats to OpenAI Model type
- Filter models based on configuration when fetch_models=false
- Return full model list when fetch_models=true

## 5. Implementation Requirements
- Base provider client class
- Provider-specific implementations for model fetching
- Provider manager for client instantiation and management
- Maintain type safety with OpenAI's type system