===========================
Provider System Overview
===========================

The provider system in GraphCap is designed to abstract the core functionalities from specific inference providers. 
This separation allows for flexibility in model inference and reduces the resources needed to run the application locally by leveraging the OpenAI API specification.

Key Objectives
==============

- **Abstraction Layer**: The provider system acts as a layer that separates the core GraphCap system from specific inference providers.
- **Flexibility**: Initially focused on transformer-based models, the system uses the OpenAI API spec for inference, allowing for flexible model integration.
- **Resource Efficiency**: By utilizing cloud-based inference, the system minimizes local resource requirements.

Configuration
=============

The provider system is configured using a TOML file (`provider.config.toml`) that defines both cloud and custom providers. This configuration file specifies the API keys, base URLs, and available models for each provider.

.. code-block:: toml

   [openai]
   kind = "openai"
   environment = "cloud"
   env_var = "OPENAI_API_KEY"
   base_url = "https://api.openai.com/v1"
   models = ["gpt-4o-mini", "gpt-4o"]
   default_model = "gpt-4o-mini"

   [gemini]
   kind = "gemini"
   environment = "cloud"
   env_var = "GOOGLE_API_KEY"
   base_url = "https://generativelanguage.googleapis.com/v1beta"
   models = ["gemini-2.0-flash-exp"]
   default_model = "gemini-2.0-flash-exp"

Provider Types
==============

1. **Cloud Providers**: These include OpenAI, Gemini, and OpenRouter, which are configured to use cloud-based APIs for inference.
2. **Custom Providers**: These include local deployments like Ollama and VLLM, which can be configured for on-premise model inference.

Usage
=====

The provider system is managed through the `ProviderManager` class, which handles the initialization and management of provider clients.

Basic Usage:
------------

.. code-block:: python
   from graphcap.providers.provider_manager import ProviderManager

   # Initialize the manager
   manager = ProviderManager("provider.config.toml")

   # Get a specific client
   openai_client = manager.get_client("openai")


Features
========

- **Unified Interface**: All providers use an OpenAI-compatible interface, simplifying integration.
- **Vision Support**: Standardized vision capabilities across providers.
- **Structured Output**: Supports JSON schema and Pydantic model outputs.
- **Configuration Management**: Centralized configuration using TOML files.
- **Error Handling**: Robust error handling with detailed logging.

For more detailed information on each component, refer to the [README.md]<../README.md> and the [provider.config.toml]<../config/provider.config.toml>.
