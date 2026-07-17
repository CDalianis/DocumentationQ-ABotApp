"""LLM factory – swap OpenAI ↔ Ollama with LLM_PROVIDER env var."""

from llama_index.core.llms import LLM
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI

from app.config import Settings, get_settings


def get_llm(settings: Settings | None = None) -> LLM:
    settings = settings or get_settings()
    provider = settings.llm_provider.lower()

    if provider == "ollama":
        return Ollama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            request_timeout=120.0,
        )

    if provider == "openai":
        return OpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
        )

    raise ValueError(f"Unknown LLM_PROVIDER: {provider!r}. Use 'openai' or 'ollama'.")
