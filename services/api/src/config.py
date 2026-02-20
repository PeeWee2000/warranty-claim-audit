"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Warranty Claim Audit API"
    debug: bool = False

    # Qdrant
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333

    # Embedding model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Scoring thresholds
    auto_approve_threshold: float = 0.8
    auto_flag_threshold: float = 0.4

    model_config = {"env_prefix": "WCA_"}


settings = Settings()
