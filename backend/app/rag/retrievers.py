"""Retriever: semantic search via ChromaDB（异步化版本）。

并发设计（压测前置优化，对齐教程）：
- asyncio.to_thread：ChromaDB 检索是阻塞文件 I/O，扔到独立线程池执行，
  不阻塞 FastAPI 事件循环，避免拖慢其他接口（登录、对话列表等）
- Semaphore(10)：最多 10 个并发检索，防止 ChromaDB 文件锁竞争
"""
import asyncio
from app.config import settings
from app.rag.vector_store import get_vector_store

# 模块级信号量：限制并发检索数，防止文件 I/O 竞争
_retrieval_semaphore = asyncio.Semaphore(10)


async def retrieve_context(query: str, top_k: int = None) -> list[dict]:
    """异步检索相关文档分块。

    返回结构：{source_id, file, chunk_text, score, full_text,
               product_category, product_name}
    """
    if top_k is None:
        top_k = settings.final_top_k

    # 阻塞的 ChromaDB 检索放到线程池，避免阻塞事件循环
    async with _retrieval_semaphore:

        def _sync_search():
            vector_store = get_vector_store()
            return vector_store.similarity_search_with_score(query, k=top_k)

        docs_with_scores = await asyncio.to_thread(_sync_search)

    results = []
    for i, (doc, score) in enumerate(docs_with_scores):
        results.append({
            "source_id": i + 1,
            "file": doc.metadata.get("source_file", "未知文件"),
            "chunk_text": doc.page_content[:300],
            "score": round(score, 4) if score else 0,
            "full_text": doc.page_content,
            "product_category": doc.metadata.get("product_category", ""),
            "product_name": doc.metadata.get("product_name", ""),
        })

    return results
