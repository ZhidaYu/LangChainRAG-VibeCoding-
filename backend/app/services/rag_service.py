"""RAG Service: orchestrates retrieval + generation + citation tracking."""
import json
import re
from typing import AsyncGenerator
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings
from app.rag.retrievers import retrieve_context
from app.rag.prompts import RAG_SYSTEM_PROMPT, RAG_USER_PROMPT
from app.rag.llm import get_llm


class RagService:
    def __init__(self):
        self.llm = get_llm(streaming=True)

    def _build_context(self, sources: list[dict]) -> str:
        """Format retrieved chunks into numbered context."""
        parts = []
        for s in sources:
            parts.append(
                f"[Source-{s['source_id']}] 文件: {s['file']}\n{s['full_text']}"
            )
        return "\n\n---\n\n".join(parts)

    def _build_history(self, messages: list) -> str:
        """Format recent conversation history."""
        if not messages:
            return "（无历史对话）"
        lines = []
        for msg in messages[-6:]:  # Last 3 turns
            role = "用户" if msg.role == "user" else "助手"
            # Truncate long messages
            content = msg.content[:300] + "..." if len(msg.content) > 300 else msg.content
            lines.append(f"{role}: {content}")
        return "\n".join(lines)

    async def query_stream(
        self, question: str, history_messages: list = None
    ) -> AsyncGenerator[str, None]:
        """Stream RAG response: retrieval -> prompt -> LLM -> yield tokens."""
        # 1. Retrieve (异步检索，不阻塞事件循环)
        sources = await retrieve_context(question)
        context = self._build_context(sources)
        history = self._build_history(history_messages or [])

        # 2. Build messages
        user_content = RAG_USER_PROMPT.format(
            context=context, history=history, question=question
        )
        messages = []
        if RAG_SYSTEM_PROMPT:
            messages.append(SystemMessage(content=RAG_SYSTEM_PROMPT))
        messages.append(HumanMessage(content=user_content))

        # 3. Stream LLM response
        # First, send sources metadata
        source_event = json.dumps({
            "type": "sources",
            "sources": [
                {
                    "source_id": s["source_id"],
                    "file": s["file"],
                    "chunk_text": s["chunk_text"],
                    "score": s["score"],
                }
                for s in sources
            ],
        }, ensure_ascii=False)
        yield f"data: {source_event}\n\n"

        # Then stream answer tokens
        answer_chunks = []
        async for chunk in self.llm.astream(messages):
            token = chunk.content
            if token:
                answer_chunks.append(token)
                token_event = json.dumps(
                    {"type": "token", "content": token}, ensure_ascii=False
                )
                yield f"data: {token_event}\n\n"

        # Done
        done_event = json.dumps({"type": "done"}, ensure_ascii=False)
        yield f"data: {done_event}\n\n"

    def extract_citations(self, answer: str, sources: list[dict]) -> list[dict]:
        """Extract which sources were actually cited in the answer."""
        cited_ids = set()
        for match in re.finditer(r"\[Source-(\d+)\]", answer):
            cited_ids.add(int(match.group(1)))

        return [
            {
                "source_id": s["source_id"],
                "file": s["file"],
                "chunk_text": s["chunk_text"],
                "score": s["score"],
            }
            for s in sources
            if s["source_id"] in cited_ids
        ]
