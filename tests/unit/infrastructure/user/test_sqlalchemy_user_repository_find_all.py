"""Tests for SQLAlchemyUserRepository.find_all."""

from datetime import datetime

import pytest

from app.domain.entities.user import User, UserRole
from app.domain.exceptions.system import DataOperationException
from app.infrastructure.database.models import UserModel
from app.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)

pytestmark = pytest.mark.anyio("asyncio")


async def test_find_all_success_returns_users(repo_db_session) -> None:
    """ユーザが存在する場合に全件のUserエンティティを返すことを確認する."""
    # Arrange
    repository = SQLAlchemyUserRepository(repo_db_session)
    now = datetime.now()
    user1 = UserModel(
        username="alice",
        email="alice@example.com",
        full_name="Alice",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    user2 = UserModel(
        username="bob",
        email="bob@example.com",
        full_name="Bob",
        role=UserRole.ADMIN,
        is_active=False,
        created_at=now,
        updated_at=now,
    )
    repo_db_session.add_all([user1, user2])
    await repo_db_session.flush()

    # Act
    users = await repository.find_all()

    # Assert
    assert isinstance(users, list)
    assert len(users) == 2
    assert all(isinstance(user, User) for user in users)
    usernames = {user.username for user in users}
    assert usernames == {"bob", "alice"}


async def test_find_all_success_returns_empty_list_when_no_users(
    repo_db_session,
) -> None:
    """ユーザが存在しない場合に空リストを返すことを確認する."""
    # Arrange
    repository = SQLAlchemyUserRepository(repo_db_session)

    # Act
    users = await repository.find_all()

    # Assert
    assert users == []


async def test_find_all_failure_sqlalchemy_error_raises_data_operation_exception(
    repo_db_session_execute_sqlalchemy_error,
) -> None:
    """SQLAlchemyError発生時にDataOperationExceptionへラップされることを確認する."""
    # Arrange
    repository = SQLAlchemyUserRepository(repo_db_session_execute_sqlalchemy_error)

    # Act / Assert
    with pytest.raises(DataOperationException) as exc_info:
        await repository.find_all()

    assert (
        exc_info.value.details.get("operation_context")
        == "SQLAlchemyUserRepository.find_all"
    )
