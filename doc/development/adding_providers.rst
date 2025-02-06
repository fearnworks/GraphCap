Adding a New Provider Integration
=================================

Overview
--------
This guide explains how to add a new provider integration into graphcap . The process
involves the following steps:

- Adding a provider configuration example in the configuration file.
- Implementing or updating a provider client (if necessary).
- Adding integration tests to verify the provider's functionality.
- Updating the provider manager if your provider requires custom initialization logic.

Prerequisites
-------------
Before you begin, ensure you have the following:
- A clear understanding of the new provider's API, credentials, and requirements.
- Familiarity with the graphcap configuration structure (TOML) and provider client design.
- A working development environment with Python 3.11+ and all required dependencies installed.

Step 1: Add Provider Configuration Example
------------------------------------------
Update the ``provider.example.config.toml`` file with a sample configuration for your new provider.
This file serves as a template for users when configuring credentials, API keys, and other provider-specific settings.

For example, add a new section similar to the following:

.. code-block:: toml

    [newprovider]
    kind = "newprovider"
    environment = "cloud"            # Use "local" if the provider is self-hosted
    env_var = "NEWPROVIDER_API_KEY"    # Environment variable storing the API key
    base_url = "https://api.newprovider.com/v1"
    models = [
        "newmodel-basic",
        "newmodel-advanced",
    ]
    default_model = "newmodel-basic"
    fetch_models = false
    # Optional rate limits configuration
    [newprovider.rate_limits]
    requests_per_minute = 15
    tokens_per_minute = 500000

Step 2: Implement or Update the Provider Client
------------------------------------------------
If the new provider requires a unique client implementation, create or update the corresponding file in
:dir:`lib/graphcap/providers/clients/`. Ensure your new client:
 
- Adheres to Python 3.11+ standards and strong typing.
- Follows the same structure and style as existing clients (e.g., :file:`openai_client.py` or :file:`gemini_client.py`).
- Implements any required endpoints and validations, such as model listing and chat completions.

If your provider uses an existing client template, you may only need to adjust endpoint URLs and method implementations.

Step 3: Update the Provider Manager (if necessary)
--------------------------------------------------
The provider manager located in :file:`lib/graphcap/providers/provider_manager.py` automatically loads
provider configurations (either from a config file or environment variables) and instantiates provider clients.

If your provider requires custom initialization logic, update the ``get_client()`` method to ensure:
 
- The new provider is recognized based on its ``kind``.
- Any additional configuration (for example, rate limits) is applied to the client.

Step 4: Add Integration Tests
-----------------------------
Integration tests help ensure the new provider works correctly and adheres to expected behaviors.
Add tests to the :dir:`tests/library_tests/provider_tests/` directory. These tests should cover:

- Client initialization and configuration validation.
- API key detection and error handling.
- Basic API calls (e.g., listing models, executing chat completions, and structured vision analysis).

For example, you might add tests resembling the following:

.. code-block:: python

    import os
    import pytest
    from graphcap.providers.clients import NewProviderClient
    from graphcap.providers.provider_manager import ProviderManager

    @pytest.mark.integration
    def test_newprovider_list_models():
        # Ensure the environment variable is set for testing
        api_key = os.getenv("NEWPROVIDER_API_KEY")
        if not api_key:
            pytest.skip("NEWPROVIDER_API_KEY not set, skipping test.")

        # Instantiate the client with test configuration
        client = NewProviderClient(
            name="newprovider",
            kind="newprovider",
            environment="cloud",
            env_var="NEWPROVIDER_API_KEY",
            base_url="https://api.newprovider.com/v1",
            default_model="newmodel-basic"
        )
        response = client.models.list()
        assert hasattr(response, "data"), "Response should have a 'data' attribute"
        assert isinstance(response.data, list), "'data' must be a list"
        assert len(response.data) > 0, "List of models should not be empty"

Review your tests by running:

.. code-block:: bash

    uv run pytest tests/library_tests/provider_tests/ -v --maxfail=1 --disable-warnings

Additional Considerations
-------------------------
- **Documentation Update:** Update the provider documentation in :file:`lib/graphcap/providers/README.md` if necessary.
- **Configuration Validation:** Leverage :mod:`pydantic` in your provider config classes to ensure robust validation.
- **Community Feedback:** Engage with collaborators via pull requests and code reviews to further refine your provider integration.

Conclusion
----------
Following this guide will help you add a new provider integration to graphcap while maintaining consistency with
existing project standards. Be sure to thoroughly test your integration and update all related documentation.

Happy coding!
