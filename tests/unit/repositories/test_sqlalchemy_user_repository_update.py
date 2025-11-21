"""Tests for SQLAlchemyUserRepository.update."""

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.domain.entities.user import User
from app.domain.exceptions.system import DataOperationException
from app.infrastructure.database.models import UserModel
from app.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)

pytestmark = pytest.mark.anyio("asyncio")


async def test_update_success_persists_changes(repo_db_session) -> None:
    """update()が既存レコードを更新することを確認する."""
    repository = SQLAlchemyUserRepository(repo_db_session)
    original = await repository.create(
        User.create(username="bob", email="bob@example.com", full_name="Bob")
    )

    original.username = "bob_updated"
    original.email = "updated@example.com"
    original.full_name = "Updated Bob"
    original.is_active = False

    updated = await repository.update(original)

    assert updated.username == "bob_updated"
    assert updated.email == "updated@example.com"
    row = await repo_db_session.get(UserModel, original.id)
    assert row is not None
    assert row.username == "bob_updated"
    assert row.email == "updated@example.com"
    assert row.full_name == "Updated Bob"
    assert row.is_active is False


async def test_update_failure_missing_id(repo_db_session) -> None:
    """ID未設定のエンティティ更新時はValueErrorとなることを確認する."""
    repository = SQLAlchemyUserRepository(repo_db_session)
    user = User.create(username="no_id", email="noid@example.com")

    with pytest.raises(ValueError, match="Cannot update user without id"):
        await repository.update(user)


async def test_update_failure_sqlalchemy_error(repo_db_session) -> None:
    """SQLAlchemyError発生時にDataOperationExceptionへラップされることを確認する."""
    repository = SQLAlchemyUserRepository(repo_db_session)
    saved = await repository.create(
        User.create(username="charlie", email="charlie@example.com")
    )

    async def _raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("forced flush failure")

    repo_db_session.flush = _raise_sqlalchemy_error  # type: ignore[assignment]
    with pytest.raises(
        DataOperationException, match="Failed to execute data operation"
    ):
        await repository.update(saved)
