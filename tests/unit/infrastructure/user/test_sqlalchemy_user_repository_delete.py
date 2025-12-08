"""Tests for SQLAlchemyUserRepository.delete."""

import pytest

from app.domain.entities.user import User
from app.domain.exceptions.system import DataOperationException
from app.infrastructure.database.models import UserModel
from app.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)

pytestmark = pytest.mark.anyio("asyncio")


async def test_delete_success_removes_user(repo_db_session) -> None:
    """delete()が既存ユーザを削除しTrueを返すことを確認する."""
    # Arrange
    repository = SQLAlchemyUserRepository(repo_db_session)
    saved = await repository.create(
        User.create(username="delete_me", email="delete@example.com")
    )

    # Act
    result = await repository.delete(saved.id)

    # Assert
    assert result is True
    assert await repo_db_session.get(UserModel, saved.id) is None


async def test_delete_failure_user_not_found_returns_false(
    repo_db_session,
) -> None:
    """存在しないID削除時にはFalseを返すことを確認する."""
    # Arrange
    repository = SQLAlchemyUserRepository(repo_db_session)

    # Act
    result = await repository.delete(user_id=999)

    # Assert
    assert result is False


async def test_delete_failure_sqlalchemy_error_raises_data_operation_exception(
    repo_db_session_delete_sqlalchemy_error,
) -> None:
    """SQLAlchemyError発生時にDataOperationExceptionへラップされることを確認する."""
    # Arrange
    repository = SQLAlchemyUserRepository(repo_db_session_delete_sqlalchemy_error)
    saved = await repository.create(
        User.create(username="broken", email="broken@example.com")
    )

    # Act / Assert
    with pytest.raises(DataOperationException) as exc_info:
        await repository.delete(saved.id)

    assert (
        exc_info.value.details.get("operation_context")
        == "SQLAlchemyUserRepository.delete"
    )
