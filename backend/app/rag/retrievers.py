"""Retriever: semantic search via ChromaDB."""
from app.config import settings
from app.rag.vector_store import get_vector_store


def retrieve_context(query: str, top_k: int = None) -> list[dict]:
    """Retrieve relevant document chunks for a query.

    Returns a list of dicts: {source_id, file, chunk_text, score}
    """
    if top_k is None:
        top_k = settings.final_top_k

    vector_store = get_vector_store()
    docs_with_scores = vector_store.similarity_search_with_score(query, k=top_k)

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
