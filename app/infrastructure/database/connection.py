from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

# Database configuration
engine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
    if settings.database_url.startswith("postgresql://")
    else settings.database_url,
    echo=False,
)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency for FastAPI."""
    async with SessionLocal() as session:
        yield session
