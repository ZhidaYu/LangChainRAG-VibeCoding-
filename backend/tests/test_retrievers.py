"""检索器单元测试（异步检索 + 信号量并发保护）。

用假向量库替换真实 ChromaDB，不依赖外部存储和嵌入 API。
"""
import asyncio
import inspect

import pytest
from langchain_core.documents import Document

from app.rag import retrievers


class FakeVectorStore:
    """记录调用参数的假向量库：返回固定文档，捕获 top_k。"""

    def __init__(self):
        self.received_k = []

    def similarity_search_with_score(self, query: str, k: int):
        self.received_k.append(k)
        docs = [
            Document(
                page_content=f"产品文档内容片段 {i}",
                metadata={
                    "source_file": f"手册{i}.pdf",
                    "product_category": "手机",
                    "product_name": f"测试手机{i}",
                },
            )
            for i in range(k)
        ]
        # ChromaDB 返回 (doc, distance) 元组列表
        return [(doc, 0.5 - i * 0.01) for i, doc in enumerate(docs)]


@pytest.fixture
def fake_store(monkeypatch):
    """把 retrieve_context 里的 get_vector_store 替换为假实现。"""
    store = FakeVectorStore()
    monkeypatch.setattr(retrievers, "get_vector_store", lambda: store)
    return store


class TestRetrieveContext:
    """异步检索函数的核心行为测试。"""

    def test_is_async_coroutine(self):
        """retrieve_context 必须是协程（async def），调用需要 await。"""
        assert inspect.iscoroutinefunction(retrievers.retrieve_context)

    @pytest.mark.asyncio
    async def test_returns_structured_results(self, fake_store):
        """返回结果结构完整：source_id 递增 + 所有字段存在。"""
        results = await retrievers.retrieve_context("测试问题", top_k=3)

        assert len(results) == 3
        for i, r in enumerate(results):
            assert r["source_id"] == i + 1  # 编号从 1 递增
            assert r["file"].endswith(".pdf")
            assert r["chunk_text"].startswith("产品文档内容片段")
            assert isinstance(r["score"], float)
            assert "full_text" in r
            assert r["product_category"] == "手机"
            assert r["product_name"].startswith("测试手机")

    @pytest.mark.asyncio
    async def test_top_k_passthrough(self, fake_store):
        """top_k 参数应原样传给向量库。"""
        await retrievers.retrieve_context("测试问题", top_k=5)
        assert fake_store.received_k == [5]

    @pytest.mark.asyncio
    async def test_default_top_k_from_settings(self, fake_store):
        """不传 top_k 时使用配置里的 FINAL_TOP_K。"""
        from app.config import settings

        await retrievers.retrieve_context("测试问题")
        assert fake_store.received_k == [settings.final_top_k]

    @pytest.mark.asyncio
    async def test_concurrent_calls_succeed(self, fake_store):
        """信号量并发保护：并发 20 次调用（超过 Semaphore(10)）应全部成功。"""
        results = await asyncio.gather(
            *[retrievers.retrieve_context(f"问题{i}", top_k=2) for i in range(20)]
        )
        assert all(len(r) == 2 for r in results)
        assert len(fake_store.received_k) == 20
