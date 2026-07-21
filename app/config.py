from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM – defaults to local Ollama (no cloud account)
    llm_provider: str = "ollama"  # "ollama" | "openai"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # Embeddings – defaults to local HuggingFace model
    embedding_provider: str = "local"  # "local" | "openai"
    openai_embedding_model: str = "text-embedding-3-small"
    local_embedding_model: str = "BAAI/bge-small-en-v1.5"

    # SQLite metadata DB (no Postgres)
    database_url: str = "sqlite+aiosqlite:///./data/docbot.db"

    # App paths
    upload_dir: str = "./uploads"
    vector_store_dir: str = "./data/vector_stores"
    chunk_size: int = 512
    chunk_overlap: int = 50
    query_cache_ttl_seconds: int = 3600
    max_upload_size_mb: int = 50

    @property
    def upload_path(self) -> Path:
        return Path(self.upload_dir)

    @property
    def vector_store_path(self) -> Path:
        return Path(self.vector_store_dir)

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
