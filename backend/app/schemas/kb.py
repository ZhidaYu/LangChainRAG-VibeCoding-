"""Knowledge Base schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    chunk_count: int
    status: str
    product_category: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class KBStatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    by_status: dict
    by_category: dict
