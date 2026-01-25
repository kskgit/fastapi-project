"""Tests for SQLAlchemyTodoRepository.delete_all_by_user_id."""

import pytest
from sqlalchemy import select

from app.domain.entities import Todo, TodoPriority
from app.domain.exceptions import DataOperationException
from app.infrastructure.database.models import TodoModel
from app.infrastructure.repositories import SQLAlchemyTodoRepository

pytestmark = pytest.mark.anyio("asyncio")


async def test_delete_all_by_user_id_success_removes_all_todos(
    repo_db_session,
) -> None:
    """delete_all_by_user_id()が指定ユーザの全Todoを削除し削除数を返すことを確認する."""
    # Arrange
    repository = SQLAlchemyTodoRepository(repo_db_session)
    user_id = 1

    # Create multiple todos for the user
    todo1 = await repository.create(
        Todo.create(
            user_id=user_id,
            title="Todo 1",
            description="First todo",
            priority=TodoPriority.high,
        )
    )
    todo2 = await repository.create(
        Todo.create(
            user_id=user_id,
            title="Todo 2",
            description="Second todo",
            priority=TodoPriority.medium,
        )
    )
    # Create a todo for a different user (should not be deleted)
    todo3 = await repository.create(
        Todo.create(
            user_id=2,
            title="Todo 3",
            description="Other user's todo",
            priority=TodoPriority.low,
        )
    )

    # Act
    delete_count = await repository.delete_all_by_user_id(user_id)

    # Assert
    assert delete_count == 2

    # Verify todos for user_id=1 are deleted
    result1 = await repo_db_session.execute(
        select(TodoModel).where(TodoModel.id == todo1.id)
    )
    assert result1.scalar_one_or_none() is None

    result2 = await repo_db_session.execute(
        select(TodoModel).where(TodoModel.id == todo2.id)
    )
    assert result2.scalar_one_or_none() is None

    # Verify todo for user_id=2 still exists
    result3 = await repo_db_session.execute(
        select(TodoModel).where(TodoModel.id == todo3.id)
    )
    assert result3.scalar_one_or_none() is not None


async def test_delete_all_by_user_id_success_returns_zero_when_no_todos(
    repo_db_session,
) -> None:
    """ユーザにTodoが存在しない場合に0を返すことを確認する."""
    # Arrange
    repository = SQLAlchemyTodoRepository(repo_db_session)
    user_id = 999

    # Act
    delete_count = await repository.delete_all_by_user_id(user_id)

    # Assert
    assert delete_count == 0


async def test_delete_all_by_user_id_failure_sqlalchemy_error_raises_data_operation_exception(  # noqa: E501
    repo_db_session_execute_sqlalchemy_error,
) -> None:
    """SQLAlchemyError発生時にDataOperationExceptionへラップされることを確認する."""
    # Arrange
    repository = SQLAlchemyTodoRepository(repo_db_session_execute_sqlalchemy_error)
    user_id = 1

    # Act / Assert
    with pytest.raises(DataOperationException) as exc_info:
        await repository.delete_all_by_user_id(user_id)

    assert (
        exc_info.value.details.get("operation_context")
        == "SQLAlchemyTodoRepository.delete_all_by_user_id"
    )
