"""Tests for SQLAlchemyTodoRepository.delete."""

import pytest
from sqlalchemy import select

from app.domain.entities.todo import Todo, TodoPriority
from app.domain.exceptions.system import DataOperationException
from app.infrastructure.database.models import TodoModel
from app.infrastructure.repositories.sqlalchemy_todo_repository import (
    SQLAlchemyTodoRepository,
)

pytestmark = pytest.mark.anyio("asyncio")


async def test_delete_success_removes_todo(repo_db_session) -> None:
    """delete()が既存Todoを削除しTrueを返すことを確認する."""
    # Arrange
    repository = SQLAlchemyTodoRepository(repo_db_session)
    saved = await repository.create(
        Todo.create(
            user_id=1,
            title="Delete Me",
            description="Will be deleted",
            priority=TodoPriority.medium,
        )
    )
    assert saved.id is not None

    # Act
    result = await repository.delete(saved.id)

    # Assert
    assert result is True
    result_query = await repo_db_session.execute(
        select(TodoModel).where(TodoModel.id == saved.id)
    )
    assert result_query.scalar_one_or_none() is None


async def test_delete_failure_todo_not_found_returns_false(
    repo_db_session,
) -> None:
    """存在しないID削除時にはFalseを返すことを確認する."""
    # Arrange
    repository = SQLAlchemyTodoRepository(repo_db_session)

    # Act
    result = await repository.delete(todo_id=999)

    # Assert
    assert result is False


async def test_delete_failure_sqlalchemy_error_raises_data_operation_exception(
    repo_db_session_delete_sqlalchemy_error,
) -> None:
    """SQLAlchemyError発生時にDataOperationExceptionへラップされることを確認する."""
    # Arrange
    repository = SQLAlchemyTodoRepository(repo_db_session_delete_sqlalchemy_error)
    saved = await repository.create(
        Todo.create(
            user_id=1,
            title="Broken",
            description="Will fail on delete",
            priority=TodoPriority.low,
        )
    )
    assert saved.id is not None

    # Act / Assert
    with pytest.raises(DataOperationException) as exc_info:
        await repository.delete(saved.id)

    assert (
        exc_info.value.details.get("operation_context")
        == "SQLAlchemyTodoRepository.delete"
    )
