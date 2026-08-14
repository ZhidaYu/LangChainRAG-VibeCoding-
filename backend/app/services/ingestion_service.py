"""Document ingestion service."""
import os
import uuid
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models.knowledge_document import KnowledgeDocument
from app.rag.loaders import load_document
from app.rag.chunking import get_text_splitter
from app.rag.vector_store import get_vector_store, reset_vector_store
from app.utils.chunk_id import generate_chunk_id
from app.utils.text_cleaner import clean_text


class IngestionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_document(
        self,
        file_path: str,
        filename: str,
        file_type: str,
        file_size: int,
        product_category: str = "",
        uploaded_by: str = "",
    ) -> KnowledgeDocument:
        """Full ingestion pipeline for a single document."""
        # 1. Create DB record
        doc = KnowledgeDocument(
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            status="processing",
            product_category=product_category or None,
            uploaded_by=uploaded_by or None,
        )
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)

        try:
            # 2. Load document
            raw_docs = load_document(file_path)

            # 3. Clean text
            for d in raw_docs:
                d.page_content = clean_text(d.page_content)
                d.metadata["source_file"] = filename
                if product_category:
                    d.metadata["product_category"] = product_category

            # 4. Chunk - use smaller chunks for structured data
            is_product = file_type in ("csv", "xlsx")
            splitter = get_text_splitter(is_product_data=is_product)
            chunks = splitter.split_documents(raw_docs)

            # 5. Generate chunk IDs and add to metadata
            for i, chunk in enumerate(chunks):
                chunk.metadata["chunk_index"] = i
                chunk.metadata["chunk_id"] = generate_chunk_id(filename, i, chunk.page_content)
                chunk.metadata["doc_id"] = doc.id

            # 6. Store in ChromaDB
            vector_store = get_vector_store()
            vector_store.add_documents(chunks)
            reset_vector_store()

            # 7. Update DB record
            doc.chunk_count = len(chunks)
            doc.status = "indexed"
            await self.db.commit()
            await self.db.refresh(doc)

            return doc

        except Exception as e:
            doc.status = "failed"
            doc.error_message = str(e)
            await self.db.commit()
            raise
