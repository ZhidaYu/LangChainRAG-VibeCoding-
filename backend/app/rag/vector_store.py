"""ChromaDB vector store wrapper."""
import os
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma
from app.config import settings
from app.rag.embeddings import get_embeddings


_collection = None


def get_vector_store() -> Chroma:
    """Get or create the ChromaDB vector store."""
    global _collection
    if _collection is not None:
        return _collection

    os.makedirs(settings.chroma_persist_dir, exist_ok=True)

    client = chromadb.PersistentClient(
        path=settings.chroma_persist_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )

    _collection = Chroma(
        client=client,
        collection_name=settings.chroma_collection_name,
        embedding_function=get_embeddings(),
    )
    return _collection


def reset_vector_store():
    """Reset the global vector store reference (used after ingestion)."""
    global _collection
    _collection = None
