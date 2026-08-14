"""Pytest fixtures for backend tests."""
import os
import sys
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Ensure backend app is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Set test environment variables BEFORE importing app
TEST_DB_PATH = "./data/test_rag.db"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB_PATH}"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["ADMIN_PASSWORD"] = "123456"
os.environ["CHROMA_PERSIST_DIR"] = "./data/chroma_test"

# Ensure data dir exists
os.makedirs("data", exist_ok=True)


def _reset_test_db():
    """Remove leftover SQLite test DB files so each test starts clean."""
    for suffix in ("", "-wal", "-shm"):
        path = TEST_DB_PATH + suffix
        if os.path.exists(path):
            os.remove(path)


@pytest_asyncio.fixture
async def client():
    """Create an async HTTP test client with database tables ready."""
    # Fresh database per test: delete stale file before first connection.
    _reset_test_db()

    from app.database import engine
    from app.models.base import Base
    from app.models.user import User  # noqa: ensure model registered
    from app.models.conversation import Conversation  # noqa
    from app.models.message import Message  # noqa
    from app.models.knowledge_document import KnowledgeDocument  # noqa

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed admin
    from app.services.auth_service import hash_password
    from app.database import AsyncSessionLocal
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.username == "admin")
        )
        if not result.scalar_one_or_none():
            session.add(User(
                username="admin",
                password_hash=hash_password("123456"),
                role="admin",
            ))
            await session.commit()

    # Now create the test app
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Cleanup
    await engine.dispose()
