"""LLM factory using DashScope (阿里云百炼)."""
from langchain_community.chat_models.tongyi import ChatTongyi
from app.config import settings


def get_llm(streaming: bool = True) -> ChatTongyi:
    """Create LLM instance using DashScope native SDK."""
    return ChatTongyi(
        model=settings.llm_model,
        dashscope_api_key=settings.dashscope_api_key,
        temperature=0.3,
        streaming=streaming,
    )
