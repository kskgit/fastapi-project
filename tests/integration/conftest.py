"""Integration test configuration and fixtures."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
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
def test_db_engine():
    """Create test database engine using in-memory SQLite."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,  # Set to True for SQL query debugging
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """Create test database session with transaction rollback."""
    TestSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )

    session = TestSessionLocal()

    yield session

    session.close()


@pytest.fixture(scope="function")
def user_repository(test_db_session: Session):
    """Create UserRepository with test database session."""
    return SQLAlchemyUserRepository(test_db_session)


@pytest.fixture(scope="function")
def todo_repository(test_db_session: Session):
    """Create TodoRepository with test database session."""
    return SQLAlchemyTodoRepository(test_db_session)


@pytest.fixture(scope="function")
def test_user(user_repository: SQLAlchemyUserRepository) -> User:
    """Create test user for todo creation tests."""
    user = User.create(
        username="test_user", email="test@example.com", full_name="Test User"
    )
    return user_repository.save(user)


@pytest.fixture(scope="function")
def test_user_id(test_user: User) -> int:
    """Return test user ID for convenience."""
    assert test_user.id is not None
    return test_user.id
