"""Tests for SQLAlchemyUserRepository.find_by_username."""

import pytest

from app.domain.entities.user import User
from app.domain.exceptions.system import DataOperationException
from app.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)

pytestmark = pytest.mark.anyio("asyncio")


async def test_find_by_username_success_returns_user(repo_db_session) -> None:
    """ユーザが存在する場合にUserエンティティを返すことを確認する."""
    # Arrange
    repository = SQLAlchemyUserRepository(repo_db_session)
    saved = await repository.create(
        User.create(username="alice", email="alice@example.com", full_name="Alice")
    )
    assert saved.username == "alice"

    # Act
    result = await repository.find_by_username("alice")

    # Assert
    assert result is not None
    assert isinstance(result, User)
    assert result.id == saved.id
    assert result.username == "alice"
    assert result.email == "alice@example.com"
    assert result.full_name == "Alice"


async def test_find_by_username_success_returns_none_when_not_found(
    repo_db_session,
) -> None:
    """ユーザが存在しない場合にNoneを返すことを確認する."""
    # Arrange
    repository = SQLAlchemyUserRepository(repo_db_session)

    # Act
    result = await repository.find_by_username("nonexistent")

    # Assert
    assert result is None


async def test_find_by_username_failure_sqlalchemy_error_raises_data_operation_exception(  # noqa: E501
    repo_db_session_execute_sqlalchemy_error,
) -> None:
    """SQLAlchemyError発生時にDataOperationExceptionへラップされることを確認する."""
    # Arrange
    repository = SQLAlchemyUserRepository(repo_db_session_execute_sqlalchemy_error)

    # Act / Assert
    with pytest.raises(DataOperationException) as exc_info:
        await repository.find_by_username("test")

    assert (
        exc_info.value.details.get("operation_context")
        == "SQLAlchemyUserRepository.find_by_username"
    )
