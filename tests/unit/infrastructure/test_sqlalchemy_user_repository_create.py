"""Tests for SQLAlchemyUserRepository.create."""

import pytest

from app.domain.entities.user import User, UserRole
from app.domain.exceptions.system import DataOperationException
from app.infrastructure.database.models import UserModel
from app.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)

pytestmark = pytest.mark.anyio("asyncio")


async def test_create_success_persists_user(repo_db_session) -> None:
    """create()がID採番後のユーザエンティティを返すことを確認する."""
    # Arrange
    repository = SQLAlchemyUserRepository(repo_db_session)
    user = User.create(username="alice", email="alice@example.com", full_name="Alice")

    # Act
    saved = await repository.create(user)

    # Assert
    assert saved.id is not None
    row = await repo_db_session.get(UserModel, saved.id)
    assert row is not None
    assert row.username == "alice"
    assert row.email == "alice@example.com"
    assert row.full_name == "Alice"
    assert row.role == UserRole.MEMBER
    assert row.is_active is True


async def test_create_failure_sqlalchemy_error(
    repo_db_session_sqlalchemy_error,
) -> None:
    """SQLAlchemyError発生時にDataOperationExceptionへラップされることを確認する."""
    # Arrange
    repository = SQLAlchemyUserRepository(repo_db_session_sqlalchemy_error)
    user = User.create(username="error", email="error@example.com")

    # Act / Assert
    with pytest.raises(
        DataOperationException, match="Failed to execute data operation"
    ):
        await repository.create(user)
