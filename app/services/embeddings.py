"""Embedding factory – swap OpenAI ↔ local sentence-transformers."""

from llama_index.core.embeddings import BaseEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding

from app.config import Settings, get_settings


def get_embed_model(settings: Settings | None = None) -> BaseEmbedding:
    settings = settings or get_settings()
    provider = settings.embedding_provider.lower()

    if provider == "local":
        return HuggingFaceEmbedding(model_name=settings.local_embedding_model)

    if provider == "openai":
        return OpenAIEmbedding(
            model=settings.openai_embedding_model,
            api_key=settings.openai_api_key,
        )

    raise ValueError(
        f"Unknown EMBEDDING_PROVIDER: {provider!r}. Use 'openai' or 'local'."
    )
