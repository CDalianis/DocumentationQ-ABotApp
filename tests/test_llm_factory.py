from unittest.mock import patch

import pytest

from app.config import Settings
from app.services.llm import get_llm


def test_llm_factory_openai():
    settings = Settings(llm_provider="openai", openai_api_key="sk-test", openai_model="gpt-4o-mini")
    with patch("app.services.llm.OpenAI") as mock_openai:
        get_llm(settings)
        mock_openai.assert_called_once_with(model="gpt-4o-mini", api_key="sk-test")


def test_llm_factory_ollama():
    settings = Settings(
        llm_provider="ollama",
        ollama_base_url="http://localhost:11434",
        ollama_model="llama3",
    )
    with patch("app.services.llm.Ollama") as mock_ollama:
        get_llm(settings)
        mock_ollama.assert_called_once_with(
            model="llama3",
            base_url="http://localhost:11434",
            request_timeout=120.0,
        )


def test_llm_factory_unknown_provider():
    settings = Settings(llm_provider="invalid")
    with pytest.raises(ValueError, match="Unknown LLM_PROVIDER"):
        get_llm(settings)
