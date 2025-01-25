import base64
import os
from pathlib import Path

import httpx
import pytest
from dotenv import load_dotenv
from GraphCap.providers.gemini_client import GeminiClient
from GraphCap.providers.ollama_client import OllamaClient
from GraphCap.providers.openai_client import OpenAIClient
from GraphCap.providers.openrouter_client import OpenRouterClient
from GraphCap.providers.provider_manager import ProviderManager
from GraphCap.providers.vllm_client import VLLMClient

# Load environment variables from .env
load_dotenv()


@pytest.fixture
def provider_manager():
    return ProviderManager("./tests/provider.test.config.toml")


@pytest.mark.integration
class TestGeminiProvider:
    @pytest.fixture(autouse=True)
    def check_gemini_api_key(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            pytest.skip("No GOOGLE_API_KEY found. Skipping Gemini tests.")

    def test_gemini_chat_completion(self, test_logger):
        client = GeminiClient(
            api_key=os.getenv("GOOGLE_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta"
        )
        completion = client.chat.completions.create(
            model="gemini-2.0-flash-exp",
            messages=[{"role": "user", "content": "Say hello in 5 words or less."}],
            max_tokens=20,
        )

        # Log the response
        test_logger("gemini_chat_completion", completion.model_dump())

        assert hasattr(completion, "choices"), "Should have 'choices' attribute"
        assert len(completion.choices) > 0, "Should have at least one choice"
        assert hasattr(completion.choices[0], "message"), "Choice should have a message"
        assert isinstance(completion.choices[0].message.content, str), "Message should be string"
        assert len(completion.choices[0].message.content) > 0, "Message should not be empty"

    def test_gemini_vision(self, test_logger):
        """Test Gemini's multimodal capabilities"""
        client = GeminiClient(
            api_key=os.getenv("GOOGLE_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta"
        )

        # Get test image
        image_path = Path(__file__).parent / "test_image.png"

        completion = client.vision(
            prompt="What's in this image? Describe it briefly.",
            image=image_path,
            model="gemini-2.0-flash-exp",
            max_tokens=100,
        )

        # Log the response
        test_logger("gemini_vision", completion.model_dump())

        assert hasattr(completion, "choices"), "Should have 'choices' attribute"
        assert len(completion.choices) > 0, "Should have at least one choice"
        assert hasattr(completion.choices[0], "message"), "Choice should have a message"
        assert isinstance(completion.choices[0].message.content, str), "Message should be string"
        assert len(completion.choices[0].message.content) > 0, "Message should not be empty"


@pytest.mark.integration
class TestOllamaProvider:
    @pytest.fixture(autouse=True)
    def check_ollama_available(self):
        # Ollama typically doesn't need an API key, but we should check if the service is available
        try:
            client = OllamaClient(api_key="", base_url="http://localhost:11434")
            client.models()
        except Exception:
            pytest.skip("Ollama service not available. Skipping Ollama tests.")

    def test_ollama_chat_completion(self):
        client = OllamaClient(api_key="", base_url="http://localhost:11434")
        completion = client.chat.completions.create(
            model="llama2",  # Using a common default model
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
    def check_vllm_available(self):
        base_url = os.getenv("VLLM_BASE_URL", "http://localhost:11435")
        try:
            # Don't try to make a models request since VLLM might not support it
            client = VLLMClient(api_key=None, base_url=base_url)  # Changed to None
            # Simple health check
            with httpx.Client() as client:
                response = client.get(f"{base_url}/health")
                if response.status_code != 200:
                    raise ConnectionError("VLLM health check failed")
        except Exception as e:
            pytest.skip(f"VLLM service not available. Error: {str(e)}")

    def test_vllm_chat_completion(self):
        base_url = os.getenv("VLLM_BASE_URL", "http://localhost:11435")
        client = VLLMClient(api_key=None, base_url=base_url)  # Changed to None
        completion = client.chat.completions.create(
            model="vision-worker",
            messages=[{"role": "user", "content": "Say hello in 5 words or less."}],
            max_tokens=20,
        )

        assert hasattr(completion, "choices"), "Should have 'choices' attribute"
        assert len(completion.choices) > 0, "Should have at least one choice"
        assert hasattr(completion.choices[0], "message"), "Choice should have a message"
        assert isinstance(completion.choices[0].message.content, str), "Message should be string"
        assert len(completion.choices[0].message.content) > 0, "Message should not be empty"

    def test_vllm_vision(self, test_logger):
        """Test VLLM's vision capabilities"""
        base_url = os.getenv("VLLM_BASE_URL", "http://localhost:11435")
        client = VLLMClient(api_key=None, base_url=base_url)

        # Get test image
        image_path = Path(__file__).parent / "test_image.png"

        completion = client.vision(
            prompt="What's in this image? Describe it briefly.", image=image_path, model="vision-worker", max_tokens=100
        )

        # Log the response
        test_logger("vllm_vision", completion.model_dump())

        assert hasattr(completion, "choices"), "Should have 'choices' attribute"
        assert len(completion.choices) > 0, "Should have at least one choice"
        assert hasattr(completion.choices[0], "message"), "Choice should have a message"
        assert isinstance(completion.choices[0].message.content, str), "Message should be string"
        assert len(completion.choices[0].message.content) > 0, "Message should not be empty"


@pytest.mark.integration
class TestOpenRouterProvider:
    @pytest.fixture(autouse=True)
    def check_openrouter_api_key(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            pytest.skip("No OPENROUTER_API_KEY found. Skipping OpenRouter tests.")

    def test_openrouter_chat_completion(self):
        client = OpenRouterClient(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            app_url=os.getenv("APP_URL"),
            app_title=os.getenv("APP_TITLE"),
        )
        completion = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hello in 5 words or less."}],
            max_tokens=20,
        )

        assert hasattr(completion, "choices"), "Should have 'choices' attribute"
        assert len(completion.choices) > 0, "Should have at least one choice"
        assert hasattr(completion.choices[0], "message"), "Choice should have a message"
        assert isinstance(completion.choices[0].message.content, str), "Message should be string"
        assert len(completion.choices[0].message.content) > 0, "Message should not be empty"

    def test_openrouter_models(self):
        client = OpenRouterClient(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")
        models = client.get_available_models()

        assert hasattr(models, "data"), "Should have 'data' attribute"
        assert len(models.data) > 0, "Should have at least one model"

        # Check if common models are available
        model_ids = [model.id for model in models.data]
        assert any("gpt" in model_id for model_id in model_ids), "Should have GPT models available"

    def test_openrouter_vision(self, test_logger):
        """Test OpenRouter's vision capabilities"""
        client = OpenRouterClient(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            app_url=os.getenv("APP_URL"),
            app_title=os.getenv("APP_TITLE"),
        )

        # Get test image
        image_path = Path(__file__).parent / "test_image.png"

        completion = client.vision(
            prompt="What's in this image? Describe it briefly.",
            image=image_path,
            model="google/gemini-2.0-flash-exp:free",  # Using a free vision model
        )

        # Log the response
        test_logger("openrouter_vision", completion.model_dump())

        assert hasattr(completion, "choices"), "Should have 'choices' attribute"
        assert len(completion.choices) > 0, "Should have at least one choice"
        assert hasattr(completion.choices[0], "message"), "Choice should have a message"
        assert isinstance(completion.choices[0].message.content, str), "Message should be string"
        assert len(completion.choices[0].message.content) > 0, "Message should not be empty"


@pytest.mark.integration
def test_provider_manager_initialization(provider_manager):
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


def get_base64_image(image_path: str) -> str:
    """Helper function to convert image to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


@pytest.mark.integration
class TestOpenAIVisionProvider:
    @pytest.fixture(autouse=True)
    def check_openai_api_key(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("No OPENAI_API_KEY found. Skipping OpenAI Vision tests.")

    def test_gpt4_vision(self, test_logger):
        """Test GPT-4 Vision capabilities"""
        client = OpenAIClient(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.openai.com/v1")

        # Get test image
        image_path = Path(__file__).parent / "test_image.png"

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": client._format_vision_content(
                        "What's in this image? Describe it briefly.", client._get_base64_image(image_path)
                    ),
                }
            ],
            max_tokens=300,
        )

        # Log the response
        test_logger("openai_vision", completion.model_dump())

        assert completion.choices[0].message.content, "Expected non-empty response"
