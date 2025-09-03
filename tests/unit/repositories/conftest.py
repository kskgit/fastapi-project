"""Repository unit test configuration and fixtures."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.infrastructure.database.models import Base


@pytest.fixture(scope="function")
async def in_memory_engine():
    """Create in-memory SQLite engine for repository unit tests."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        pool_pre_ping=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def repo_db_session(in_memory_engine):
    """Create database session for repository unit tests."""
    AsyncSessionLocal = async_sessionmaker(
        in_memory_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with AsyncSessionLocal() as session:
        yield session
