"""API router aggregation."""
from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.conversations import router as conversations_router
from app.api.chat import router as chat_router
from app.api.kb import router as kb_router
from app.api.users import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(conversations_router, prefix="/conversations", tags=["对话管理"])
api_router.include_router(chat_router, prefix="/chat", tags=["问答"])
api_router.include_router(kb_router, prefix="/kb", tags=["知识库管理"])
api_router.include_router(users_router, prefix="/users", tags=["用户管理"])
