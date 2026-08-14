"""FastAPI application entry point."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, AsyncSessionLocal
from app.models.base import Base
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.knowledge_document import KnowledgeDocument
from app.api.router import api_router
from app.middleware.error_handler import register_exception_handlers
from app.middleware.logger import LoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/Shutdown events."""
    # Startup: create tables and seed admin
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/chroma", exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed admin user
    from passlib.context import CryptContext
    from sqlalchemy import select

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.username == settings.admin_username)
        )
        admin = result.scalar_one_or_none()
        if not admin:
            admin = User(
                username=settings.admin_username,
                password_hash=pwd_context.hash(settings.admin_password),
                role="admin",
            )
            session.add(admin)
            await session.commit()

    yield

    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="电商RAG知识库问答系统",
    description="LangChain RAG Enterprise Knowledge Base Q&A System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(LoggingMiddleware)
register_exception_handlers(app)

# Routes
app.include_router(api_router, prefix="/api")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    from sqlalchemy import select as sa_select
    # Check DB
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(sa_select(User).limit(1))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"

    # Check ChromaDB
    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        client.heartbeat()
        chroma_status = "ok"
    except Exception as e:
        chroma_status = f"error: {str(e)}"

    return {
        "status": "ok",
        "database": db_status,
        "chromadb": chroma_status,
    }
