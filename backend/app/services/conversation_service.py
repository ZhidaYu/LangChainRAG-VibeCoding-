"""Conversation service."""
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.conversation import Conversation
from app.models.message import Message


class ConversationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_conversations(
        self, user_id: str, page: int = 1, size: int = 20
    ) -> list[Conversation]:
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id, Conversation.is_active == 1)
            .order_by(desc(Conversation.updated_at))
            .offset((page - 1) * size)
            .limit(size)
        )
        return list(result.scalars().all())

    async def create_conversation(
        self, user_id: str, title: Optional[str] = None
    ) -> Conversation:
        conv = Conversation(user_id=user_id)
        if title:
            conv.title = title
        self.db.add(conv)
        await self.db.commit()
        await self.db.refresh(conv)
        return conv

    async def get_conversation(self, conv_id: str) -> Optional[Conversation]:
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conv_id)
        )
        return result.scalar_one_or_none()

    async def get_messages(self, conv_id: str) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conv_id)
            .order_by(Message.created_at)
        )
        return list(result.scalars().all())

    async def delete_conversation(self, conv_id: str) -> bool:
        conv = await self.get_conversation(conv_id)
        if not conv:
            return False
        conv.is_active = 0
        await self.db.commit()
        return True

    async def update_title(self, conv_id: str, title: str) -> Optional[Conversation]:
        conv = await self.get_conversation(conv_id)
        if not conv:
            return None
        conv.title = title
        await self.db.commit()
        await self.db.refresh(conv)
        return conv

    async def save_message(
        self,
        conv_id: str,
        role: str,
        content: str,
        sources: str = "[]",
        token_count: Optional[int] = None,
    ) -> Message:
        msg = Message(
            conversation_id=conv_id,
            role=role,
            content=content,
            sources=sources,
            token_count=token_count,
        )
        self.db.add(msg)
        # Update conversation updated_at
        conv = await self.get_conversation(conv_id)
        if conv:
            conv.updated_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(msg)
        return msg

    async def update_conversation_title(self, conv_id: str, title: str):
        conv = await self.get_conversation(conv_id)
        if conv:
            conv.title = title
            await self.db.commit()
