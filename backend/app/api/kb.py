"""Knowledge Base management API (admin only)."""
import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.dependencies import require_admin
from app.models.user import User
from app.models.knowledge_document import KnowledgeDocument
from app.schemas.kb import DocumentResponse, KBStatsResponse
from app.services.ingestion_service import IngestionService
from app.config import settings

router = APIRouter()

UPLOAD_DIR = Path("data/raw")
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".csv", ".xlsx"}


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    product_category: str = Form(""),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Upload and ingest a document."""
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {ext}。支持的格式: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Save file
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = UPLOAD_DIR / unique_name

    content = await file.read()
    file_path.write_bytes(content)

    # Ingest
    svc = IngestionService(db)
    try:
        doc = await svc.process_document(
            file_path=str(file_path),
            filename=file.filename,
            file_type=ext.lstrip("."),
            file_size=len(content),
            product_category=product_category,
            uploaded_by=admin.id,
        )
        return {
            "detail": "文档处理完成" if doc.status == "indexed" else f"处理状态: {doc.status}",
            "document_id": doc.id,
            "status": doc.status,
            "chunk_count": doc.chunk_count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档处理失败: {str(e)}")


@router.get("/documents", response_model=list[DocumentResponse])
async def list_documents(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: str = Query(""),
    product_category: str = Query(""),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all knowledge documents."""
    stmt = select(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc())

    if status:
        stmt = stmt.where(KnowledgeDocument.status == status)
    if product_category:
        stmt = stmt.where(KnowledgeDocument.product_category == product_category)

    stmt = stmt.offset((page - 1) * size).limit(size)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get a single document's details."""
    result = await db.execute(
        select(KnowledgeDocument).where(KnowledgeDocument.id == doc_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return doc


@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete a document and its vectors from ChromaDB."""
    result = await db.execute(
        select(KnowledgeDocument).where(KnowledgeDocument.id == doc_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    # Delete vectors from ChromaDB
    try:
        from app.rag.vector_store import get_vector_store, reset_vector_store
        vs = get_vector_store()
        # Delete by doc_id metadata filter
        vs._collection.delete(where={"doc_id": doc_id})
        reset_vector_store()
    except Exception:
        pass  # Vector deletion is best-effort

    await db.delete(doc)
    await db.commit()
    return {"detail": "文档已删除"}


@router.get("/stats", response_model=KBStatsResponse)
async def get_stats(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get knowledge base statistics."""
    # Total documents
    total_result = await db.execute(
        select(func.count(KnowledgeDocument.id))
    )
    total_docs = total_result.scalar()

    # Total chunks
    chunks_result = await db.execute(
        select(func.sum(KnowledgeDocument.chunk_count))
    )
    total_chunks = chunks_result.scalar() or 0

    # By status
    by_status = {}
    for s in ("processing", "indexed", "failed"):
        r = await db.execute(
            select(func.count()).where(KnowledgeDocument.status == s)
        )
        by_status[s] = r.scalar()

    # By category
    by_cat = {}
    cat_result = await db.execute(
        select(
            KnowledgeDocument.product_category,
            func.count(KnowledgeDocument.id),
        )
        .where(KnowledgeDocument.product_category.isnot(None))
        .group_by(KnowledgeDocument.product_category)
    )
    for cat, cnt in cat_result.all():
        by_cat[cat] = cnt

    return KBStatsResponse(
        total_documents=total_docs,
        total_chunks=total_chunks,
        by_status=by_status,
        by_category=by_cat,
    )
