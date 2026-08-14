"""Embedding model wrapper using DashScope (阿里云百炼) - native SDK."""
from langchain_community.embeddings import DashScopeEmbeddings
from app.config import settings


def get_embeddings() -> DashScopeEmbeddings:
    """Create embedding model instance using DashScope native SDK."""
    return DashScopeEmbeddings(
        model=settings.embedding_model,
        dashscope_api_key=settings.dashscope_api_key,
    )
