"""E2E test configuration and fixtures."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.domain.entities.user import User
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models import Base
from app.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from main import app


@pytest.fixture(scope="function")
async def in_memory_engine():
    """Create in-memory SQLite engine for e2e tests."""
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
async def test_db_session(in_memory_engine):
    """Create test database session."""
    AsyncSessionLocal = async_sessionmaker(
        in_memory_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
async def test_user(test_db_session):
    """Create test user for e2e tests."""
    user_repo = SQLAlchemyUserRepository(test_db_session)

    user = User.create(
        username="e2e_test_user",
        email="e2e@example.com",
        full_name="E2E Test User",
    )

    saved_user = await user_repo.save(user)
    await test_db_session.commit()
    return saved_user


@pytest.fixture(scope="function")
async def test_client(test_db_session):
    """Create HTTPx test client with dependency overrides."""

    async def get_test_db_session():
        return test_db_session

    # Override database dependency
    app.dependency_overrides[get_db] = get_test_db_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client

    # Clean up dependency overrides
    app.dependency_overrides.clear()
