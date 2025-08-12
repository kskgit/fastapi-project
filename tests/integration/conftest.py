"""Async Integration test configuration and fixtures."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.domain.entities.user import User
from app.infrastructure.database.connection import Base
from app.infrastructure.repositories.sqlalchemy_todo_repository import (
    SQLAlchemyTodoRepository,
)
from app.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)


@pytest.fixture(scope="function")
async def async_test_db_engine():
    """Create async test database engine using in-memory SQLite."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,  # Set to True for SQL query debugging
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="function")
async def async_test_db_session(async_test_db_engine):
    """Create async test database session with transaction rollback."""
    AsyncTestSessionLocal = async_sessionmaker(
        async_test_db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncTestSessionLocal() as session:
        yield session
        await session.close()


@pytest.fixture(scope="function")
async def async_user_repository(async_test_db_session: AsyncSession):
    """Create UserRepository with test database session."""
    return SQLAlchemyUserRepository(async_test_db_session)


@pytest.fixture(scope="function")
async def async_todo_repository(async_test_db_session: AsyncSession):
    """Create TodoRepository with test database session."""
    return SQLAlchemyTodoRepository(async_test_db_session)


@pytest.fixture(scope="function")
async def async_test_user(async_user_repository: SQLAlchemyUserRepository) -> User:
    """Create test user for async todo creation tests."""
    user = User.create(
        username="async_test_user",
        email="asynctest@example.com",
        full_name="Async Test User",
    )
    return await async_user_repository.save(user)


@pytest.fixture(scope="function")
async def async_test_user_id(async_test_user: User) -> int:
    """Return async test user ID for convenience."""
    assert async_test_user.id is not None
    return async_test_user.id
