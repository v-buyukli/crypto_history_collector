from collections.abc import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings


# Sync
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)


def get_sync_session() -> Session:
    """Create synchronous database session."""
    return SessionLocal()


# Async
async_engine = create_async_engine(settings.async_database_url)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession]:
    """Async database session dependency."""
    async with AsyncSessionLocal() as session:
        yield session
