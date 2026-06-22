"""Typed settings loaded from environment variables."""

from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env and process environment."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_temperature: float = 0.1
    groq_max_tokens: int = 2048
    groq_timeout: int = 30

    cerebras_api_key: str = ""
    cerebras_model: str = "llama-3.3-70b"
    cerebras_base_url: str = "https://api.cerebras.ai/v1"

    google_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    llm_provider_order: str = "groq,cerebras,gemini,ollama"

    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    embedding_batch_size: int = 64
    embedding_device: str = "cpu"

    chroma_persist_dir: str = "./data/chroma_db"
    chroma_collection: str = "personal_knowledge"
    chroma_distance_metric: str = "cosine"

    retrieval_top_k: int = 10
    similarity_threshold: float = 0.3

    chunk_size: int = 512
    chunk_overlap: int = 50
    min_chunk_size: int = 50

    raw_data_dir: str = "./data/raw"
    processed_data_dir: str = "./data/processed"
    sqlite_path: str = "./data/sqlite/metadata.db"
    conversations_db_path: str = "./data/sqlite/conversations.db"

    watch_enabled: bool = True
    watch_directory: str = "./data/raw"
    watch_debounce_seconds: int = 2

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    log_level: str = "INFO"
    log_format: str = "json"

    @property
    def provider_list(self) -> List[str]:
        return [p.strip().lower() for p in self.llm_provider_order.split(",") if p.strip()]

    @property
    def available_providers(self) -> List[str]:
        available: list[str] = []
        for provider in self.provider_list:
            if provider == "groq" and self.groq_api_key:
                available.append(provider)
            elif provider == "cerebras" and self.cerebras_api_key:
                available.append(provider)
            elif provider == "gemini" and self.google_api_key:
                available.append(provider)
            elif provider == "ollama":
                available.append(provider)
        return available

    @field_validator("chunk_size")
    @classmethod
    def validate_chunk_size(cls, value: int) -> int:
        if value < 100 or value > 5000:
            raise ValueError("chunk_size must be between 100 and 5000")
        return value

    @field_validator("chunk_overlap")
    @classmethod
    def validate_chunk_overlap(cls, value: int) -> int:
        if value < 0:
            raise ValueError("chunk_overlap must be non-negative")
        return value

    def ensure_directories(self) -> None:
        dirs = [
            self.raw_data_dir,
            self.processed_data_dir,
            self.chroma_persist_dir,
            Path(self.sqlite_path).parent,
            Path(self.conversations_db_path).parent,
            "./data/cache",
        ]
        for directory in dirs:
            Path(directory).mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
