"""Application configuration via Pydantic Settings."""
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """App settings loaded from .env file."""

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/rag_ecommerce.db"

    # ChromaDB
    chroma_persist_dir: str = "./data/chroma"
    chroma_collection_name: str = "ecommerce_kb"

    # DashScope (阿里云百炼)
    dashscope_api_key: str = ""
    llm_model: str = "qwen-plus"
    embedding_model: str = "text-embedding-v3"
    dashscope_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # JWT
    jwt_secret_key: str = "change-me"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # Admin seed
    admin_username: str = "admin"
    admin_password: str = "123456"

    # CORS
    cors_origins: str = "http://localhost:5173"

    # RAG params
    chunk_size: int = 500
    chunk_overlap: int = 100
    retrieval_top_k: int = 10
    final_top_k: int = 5
    cache_ttl_seconds: int = 3600

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
