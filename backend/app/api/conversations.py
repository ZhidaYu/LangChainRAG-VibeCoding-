"""Conversation API routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    MessageResponse,
)
from app.services.conversation_service import ConversationService

router = APIRouter()


@router.get("", response_model=list[ConversationResponse])
async def list_conversations(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = ConversationService(db)
    return await svc.list_conversations(current_user.id, page, size)


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    req: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = ConversationService(db)
    return await svc.create_conversation(current_user.id, req.title)


@router.get("/{conv_id}", response_model=list[MessageResponse])
async def get_messages(
    conv_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = ConversationService(db)
    conv = await svc.get_conversation(conv_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="对话不存在")
    return await svc.get_messages(conv_id)


@router.delete("/{conv_id}")
async def delete_conversation(
    conv_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = ConversationService(db)
    conv = await svc.get_conversation(conv_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="对话不存在")
    await svc.delete_conversation(conv_id)
    return {"detail": "删除成功"}


@router.put("/{conv_id}", response_model=ConversationResponse)
async def update_conversation(
    conv_id: str,
    req: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = ConversationService(db)
    conv = await svc.get_conversation(conv_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="对话不存在")
    updated = await svc.update_title(conv_id, req.title)
    return updated
