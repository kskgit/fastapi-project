"""Repository unit test configuration and fixtures."""

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.infrastructure.database.connection import Base


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


@pytest.fixture(scope="function")
async def repo_db_session_sqlalchemy_error(in_memory_engine):
    """Session fixture that forces SQLAlchemyError on flush for failure-path tests."""
    AsyncSessionLocal = async_sessionmaker(
        in_memory_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with AsyncSessionLocal() as session:

        async def _raise_sqlalchemy_error(*args, **kwargs):
            raise SQLAlchemyError("forced SQLAlchemyError for test")

        session.flush = _raise_sqlalchemy_error  # type: ignore[assignment]
        yield session


@pytest.fixture(scope="function")
async def repo_db_session_delete_sqlalchemy_error(in_memory_engine):
    """Session fixture that forces SQLAlchemyError on delete for failure tests."""
    AsyncSessionLocal = async_sessionmaker(
        in_memory_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with AsyncSessionLocal() as session:

        async def _raise_sqlalchemy_error(*args, **kwargs):
            raise SQLAlchemyError("forced SQLAlchemyError on delete for test")

        session.delete = _raise_sqlalchemy_error  # type: ignore[assignment]
        yield session
