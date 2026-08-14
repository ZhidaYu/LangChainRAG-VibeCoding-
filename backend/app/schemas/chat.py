"""Chat request/response schemas."""
from typing import Optional
from pydantic import BaseModel


class ChatQueryRequest(BaseModel):
    conversation_id: Optional[str] = None
    question: str
