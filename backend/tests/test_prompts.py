"""Tests for RAG prompt templates."""
from langchain_core.prompts import ChatPromptTemplate

from app.rag.prompts import get_rag_prompt, RAG_USER_PROMPT, RAG_SYSTEM_PROMPT


class TestRagPrompt:
    """RAG prompt template tests."""

    def test_get_rag_prompt_returns_chat_prompt(self):
        """Should return a ChatPromptTemplate instance."""
        prompt = get_rag_prompt()
        assert isinstance(prompt, ChatPromptTemplate)

    def test_user_prompt_has_all_placeholders(self):
        """Template must contain context/history/question placeholders."""
        assert "{context}" in RAG_USER_PROMPT
        assert "{history}" in RAG_USER_PROMPT
        assert "{question}" in RAG_USER_PROMPT

    def test_format_fills_context_and_question(self):
        """Formatted messages should embed context and question."""
        prompt = get_rag_prompt()
        messages = prompt.format_messages(
            context="商品A售价99元", history="无", question="商品A多少钱？"
        )
        assert len(messages) == 1
        content = messages[0].content
        assert isinstance(content, str)
        assert "商品A售价99元" in content
        assert "商品A多少钱？" in content

    def test_system_prompt_is_string(self):
        """System prompt should be a plain string (currently neutral mode)."""
        assert isinstance(RAG_SYSTEM_PROMPT, str)
