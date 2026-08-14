"""SQLAlchemy database engine and session setup.

并发加固说明（压力测试前优化）：
- pool_size 10→20、max_overflow 5→10：容纳更多并发连接
- connect_args timeout=30：SQLite 写锁等待 30 秒而非立即报 "database is locked"
- WAL 模式：读写不互斥，读操作不再阻塞写操作（在 lifespan 中通过 PRAGMA 启用）
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from app.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=20,
    max_overflow=10,
    connect_args={"timeout": 30} if settings.database_url.startswith("sqlite") else {},
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def enable_wal_mode() -> None:
    """启用 SQLite WAL 模式：读操作和写操作互不阻塞，大幅提升并发读写能力。

    在应用启动时（lifespan）调用一次即可，设置对数据库文件持久生效。
    """
    if not settings.database_url.startswith("sqlite"):
        return
    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA journal_mode=WAL"))
        await conn.execute(text("PRAGMA synchronous=NORMAL"))


async def get_db() -> AsyncSession:
    """Dependency: yield an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
