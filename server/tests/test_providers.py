import os
from pathlib import Path

import httpx
import pytest
from dotenv import load_dotenv
from graphcap.providers.clients import (
    GeminiClient,
    OllamaClient,
    OpenAIClient,
    OpenRouterClient,
    VLLMClient,
)
from graphcap.providers.provider_manager import ProviderManager
from graphcap.schemas.structured_vision import StructuredVisionConfig
from loguru import logger
from pydantic import BaseModel


class TestStructuredOutput(BaseModel):
    is_cat: bool
    caption: str


test_vision_config = StructuredVisionConfig(
    prompt="Is this a cat? What does it look like?", schema=TestStructuredOutput, config_name="test", version="1"
)


# Load environment variables from .env
load_dotenv()

pytestmark = pytest.mark.asyncio  # Mark all tests in module as async


@pytest.fixture(scope="function")
async def provider_manager():
    """Initialize provider manager with test config"""
    manager = ProviderManager("./tests/provider.test.config.toml")
    try:
        yield manager
    finally:
        # Add cleanup if needed
        for client in manager.clients().values():
            if hasattr(client, "aclose"):
                await client.aclose()


@pytest.fixture(scope="session")
async def http_client():
    """Fixture to provide an async HTTP client"""
    client = httpx.AsyncClient()
    try:
        yield client
    finally:
        await client.aclose()


@pytest.mark.integration
class TestGeminiProvider:
    @pytest.fixture(autouse=True)
    def check_gemini_api_key(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            pytest.skip("No GOOGLE_API_KEY found. Skipping Gemini tests.")

    async def test_gemini_chat_completion(self, test_logger, provider_manager):
        client = provider_manager.get_client("gemini")
        completion = await client.chat.completions.create(
            model=client.default_model,
            messages=[{"role": "user", "content": "Say hello in 5 words or less."}],
            max_tokens=20,
        )

        test_logger("gemini_chat_completion", completion.model_dump())

        assert hasattr(completion, "choices"), "Should have 'choices' attribute"
        assert len(completion.choices) > 0, "Should have at least one choice"
        assert hasattr(completion.choices[0], "message"), "Choice should have a message"
        assert isinstance(completion.choices[0].message.content, str), "Message should be string"
        assert len(completion.choices[0].message.content) > 0, "Message should not be empty"

    async def test_gemini_vision(self, test_logger, provider_manager):
        """Test Gemini's multimodal capabilities"""
        client = provider_manager.get_client("gemini")
        image_path = Path(__file__).parent / "test_image.png"

        completion = await client.vision(
            prompt="What's in this image? Describe it briefly.",
            image=image_path,
            model=client.default_model,
            max_tokens=100,
        )

        test_logger("gemini_vision", completion.model_dump())

        assert hasattr(completion, "choices"), "Should have 'choices' attribute"
        assert len(completion.choices) > 0, "Should have at least one choice"
        assert hasattr(completion.choices[0], "message"), "Choice should have a message"
        assert isinstance(completion.choices[0].message.content, str), "Message should be string"
        assert len(completion.choices[0].message.content) > 0, "Message should not be empty"

    async def test_gemini_structured_vision(self, test_logger, provider_manager):
        """Test Gemini's structured vision capabilities"""
        client = provider_manager.get_client("gemini")
        image_path = Path(__file__).parent / "test_image.png"
        await test_structured_vision(client, test_logger, image_path)


@pytest.mark.integration
class TestOllamaProvider:
    @pytest.fixture(autouse=True)
    async def check_ollama_available(self, provider_manager):
        try:
            client = provider_manager.get_client("ollama")
            await client.get_models()
        except Exception:
            pytest.skip("Ollama service not available. Skipping Ollama tests.")

    async def test_ollama_chat_completion(self, provider_manager):
        client = provider_manager.get_client("ollama")
        completion = await client.chat.completions.create(
            model=client.default_model,
            messages=[{"role": "user", "content": "Say hello in 5 words or less."}],
            max_tokens=20,
        )

        assert hasattr(completion, "choices"), "Should have 'choices' attribute"
        assert len(completion.choices) > 0, "Should have at least one choice"
        assert hasattr(completion.choices[0], "message"), "Choice should have a message"
        assert isinstance(completion.choices[0].message.content, str), "Message should be string"
        assert len(completion.choices[0].message.content) > 0, "Message should not be empty"


@pytest.mark.integration
class TestVLLMProvider:
    @pytest.fixture(autouse=True)
    async def check_vllm_available(self, provider_manager, http_client):
        try:
            client = provider_manager.get_client("vllm-pixtral")
            healthy = await client.health()
            print(f"VLLM health check response: {healthy}")
            if not healthy:
                raise ConnectionError("VLLM health check failed")
        except Exception as e:
            pytest.skip(f"VLLM service not available. Error: {str(e)}")

    async def test_vllm_chat_completion(self, provider_manager):
        client = provider_manager.get_client("vllm-pixtral")
        completion = await client.chat.completions.create(
            model=client.default_model,
            messages=[{"role": "user", "content": "Say hello in 5 words or less."}],
            max_tokens=20,
        )

        assert hasattr(completion, "choices"), "Should have 'choices' attribute"
        assert len(completion.choices) > 0, "Should have at least one choice"
        assert hasattr(completion.choices[0], "message"), "Choice should have a message"
        assert isinstance(completion.choices[0].message.content, str), "Message should be string"
        assert len(completion.choices[0].message.content) > 0, "Message should not be empty"

    async def test_vllm_vision(self, test_logger, provider_manager):
        """Test VLLM's vision capabilities"""
        client = provider_manager.get_client("vllm-pixtral")
        image_path = Path(__file__).parent / "test_image.png"

        completion = await client.vision(
            prompt="What's in this image? Describe it briefly.",
            image=image_path,
            model=client.default_model,
            max_tokens=100,
        )

        test_logger("vllm_vision", completion.model_dump())

        assert hasattr(completion, "choices"), "Should have 'choices' attribute"
        assert len(completion.choices) > 0, "Should have at least one choice"
        assert hasattr(completion.choices[0], "message"), "Choice should have a message"
        assert isinstance(completion.choices[0].message.content, str), "Message should be string"
        assert len(completion.choices[0].message.content) > 0, "Message should not be empty"

    async def test_vllm_structured_vision(self, test_logger, provider_manager):
        """Test VLLM's structured vision capabilities"""
        client = provider_manager.get_client("vllm-pixtral")
        image_path = Path(__file__).parent / "test_image.png"
        await test_structured_vision(client, test_logger, image_path)


@pytest.mark.integration
class TestOpenRouterProvider:
    @pytest.fixture(autouse=True)
    def check_openrouter_api_key(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            pytest.skip("No OPENROUTER_API_KEY found. Skipping OpenRouter tests.")

    async def test_openrouter_chat_completion(self, provider_manager):
        client = provider_manager.get_client("openrouter")
        try:
            completion = await client.chat.completions.create(
                model=client.default_model,
                messages=[{"role": "user", "content": "Say hello in 5 words or less."}],
                max_tokens=20,
            )
        except Exception as e:
            pytest.fail(f"OpenRouter chat completion failed: {str(e)}")

        # Add debug logging
        logger.debug(f"OpenRouter completion response: {completion}")

        assert completion is not None, "Completion should not be None"
        assert hasattr(completion, "choices"), "Should have 'choices' attribute"
        assert completion.choices is not None, "Choices should not be None"
        assert len(completion.choices) > 0, "Should have at least one choice"
        assert hasattr(completion.choices[0], "message"), "Choice should have a message"
        assert isinstance(completion.choices[0].message.content, str), "Message should be string"
        assert len(completion.choices[0].message.content) > 0, "Message should not be empty"

    async def test_openrouter_models(self, provider_manager):
        client = provider_manager.get_client("openrouter")
        models = await client.get_available_models()

        assert hasattr(models, "data"), "Should have 'data' attribute"
        assert len(models.data) > 0, "Should have at least one model"
        assert any("gpt" in model.id for model in models.data), "Should have GPT models available"

    async def test_openrouter_vision(self, test_logger, provider_manager):
        """Test OpenRouter's vision capabilities"""
        client = provider_manager.get_client("openrouter")
        image_path = Path(__file__).parent / "test_image.png"

        try:
            completion = await client.vision(
                prompt="What's in this image? Describe it briefly.",
                image=image_path,
                model=client.default_model,
            )
        except Exception as e:
            pytest.fail(f"OpenRouter vision completion failed: {str(e)}")

        test_logger("openrouter_vision", completion.model_dump())
        logger.debug(f"OpenRouter vision response: {completion}")

        assert completion is not None, "Completion should not be None"
        assert hasattr(completion, "choices"), "Should have 'choices' attribute"
        assert completion.choices is not None, "Choices should not be None"
        assert len(completion.choices) > 0, "Should have at least one choice"
        assert hasattr(completion.choices[0], "message"), "Choice should have a message"
        assert isinstance(completion.choices[0].message.content, str), "Message should be string"
        assert len(completion.choices[0].message.content) > 0, "Message should not be empty"

    async def test_openrouter_structured_vision(self, test_logger, provider_manager):
        """Test OpenRouter's structured vision capabilities"""
        client = provider_manager.get_client("openrouter")
        image_path = Path(__file__).parent / "test_image.png"
        await test_structured_vision(client, test_logger, image_path)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_provider_manager_initialization(provider_manager):
    """Test that ProviderManager can initialize and return clients"""
    clients = provider_manager.clients()
    assert clients, "Should have at least one client initialized"

    # Test specific provider availability based on config
    for provider_name, client in clients.items():
        assert client is not None, f"Client for {provider_name} should not be None"
        # Verify client is an instance of the correct type
        if "openai" in provider_name:
            assert isinstance(client, OpenAIClient)
        elif "gemini" in provider_name:
            assert isinstance(client, GeminiClient)
        elif "ollama" in provider_name:
            assert isinstance(client, OllamaClient)
        elif "vllm" in provider_name:
            assert isinstance(client, VLLMClient)
        elif "openrouter" in provider_name:
            assert isinstance(client, OpenRouterClient)


@pytest.mark.integration
class TestOpenAIVisionProvider:
    @pytest.fixture(autouse=True)
    def check_openai_api_key(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("No OPENAI_API_KEY found. Skipping OpenAI Vision tests.")

    @pytest.mark.asyncio
    async def test_gpt4_vision(self, test_logger, provider_manager):
        """Test GPT-4 Vision capabilities"""
        client = provider_manager.get_client("openai")
        image_path = Path(__file__).parent / "test_image.png"

        completion = await client.vision(
            prompt="What's in this image? Describe it briefly.",
            image=image_path,
            model=client.default_model,
            max_tokens=300,
        )

        test_logger("openai_vision", completion.model_dump())
        assert completion.choices[0].message.content, "Expected non-empty response"

    async def test_openai_structured_vision(self, test_logger, provider_manager):
        """Test OpenAI's structured vision capabilities"""
        client = provider_manager.get_client("openai")
        image_path = Path(__file__).parent / "test_image.png"
        await test_structured_vision(client, test_logger, image_path)


async def test_structured_vision(client, test_logger, image_path):
    """Helper function to test structured vision capabilities"""
    completion = await client.vision(
        prompt=test_vision_config.prompt,
        image=image_path,
        schema=test_vision_config.schema,
        model=client.default_model,
        max_tokens=100,
    )

    test_logger(f"{client.name}_structured_vision", completion.model_dump())

    # If the response is already a Pydantic model
    if isinstance(completion, TestStructuredOutput):
        assert isinstance(completion.is_cat, bool), "is_cat should be boolean"
        assert isinstance(completion.caption, str), "caption should be string"
        assert len(completion.caption) > 0, "caption should not be empty"
        return

    # For providers that return raw completion
    assert hasattr(completion, "choices"), "Should have 'choices' attribute"
    assert len(completion.choices) > 0, "Should have at least one choice"
    assert hasattr(completion.choices[0], "message"), "Choice should have a message"
    content = completion.choices[0].message.content
    assert isinstance(content, str), "Message should be string"
    assert len(content) > 0, "Message should not be empty"
