"""Tests for SQLAlchemyTodoRepository.find_with_pagination."""

import pytest

from app.domain.entities import Todo, TodoPriority, TodoStatus
from app.domain.exceptions import DataOperationException
from app.infrastructure.repositories import SQLAlchemyTodoRepository

pytestmark = pytest.mark.anyio("asyncio")


async def test_find_with_pagination_success_returns_todos(repo_db_session) -> None:
    """find_with_pagination()がページネーションされたTodoリストを返すことを確認する."""
    # Arrange
    repository = SQLAlchemyTodoRepository(repo_db_session)
    user_id = 1

    # Create multiple todos
    for i in range(5):
        await repository.create(
            Todo.create(
                user_id=user_id,
                title=f"Todo {i}",
                description=f"Description {i}",
                priority=TodoPriority.medium,
            )
        )

    # Act
    result = await repository.find_with_pagination(user_id=user_id, skip=0, limit=3)

    # Assert
    assert isinstance(result, list)
    assert len(result) == 3
    assert all(isinstance(todo, Todo) for todo in result)
    assert all(todo.user_id == user_id for todo in result)


async def test_find_with_pagination_success_with_skip(repo_db_session) -> None:
    """skipパラメータが正しく動作することを確認する."""
    # Arrange
    repository = SQLAlchemyTodoRepository(repo_db_session)
    user_id = 1

    # Create multiple todos
    for i in range(5):
        await repository.create(
            Todo.create(
                user_id=user_id,
                title=f"Todo {i}",
                priority=TodoPriority.medium,
            )
        )

    # Act
    result = await repository.find_with_pagination(user_id=user_id, skip=2, limit=3)

    # Assert
    assert len(result) == 3


async def test_find_with_pagination_success_with_status_filter(
    repo_db_session,
) -> None:
    """statusフィルタが正しく動作することを確認する."""
    # Arrange
    repository = SQLAlchemyTodoRepository(repo_db_session)
    user_id = 1

    # Create todos with different statuses
    todo1 = await repository.create(
        Todo.create(
            user_id=user_id,
            title="Pending Todo",
            priority=TodoPriority.medium,
        )
    )
    todo2 = await repository.create(
        Todo.create(
            user_id=user_id,
            title="In Progress Todo",
            priority=TodoPriority.high,
        )
    )
    # Update todo2 to in_progress
    todo2.status = TodoStatus.in_progress
    await repository.update(todo2)

    # Act
    result = await repository.find_with_pagination(
        user_id=user_id, status=TodoStatus.pending
    )

    # Assert
    assert len(result) == 1
    assert result[0].status == TodoStatus.pending
    assert result[0].id == todo1.id


async def test_find_with_pagination_success_with_priority_filter(
    repo_db_session,
) -> None:
    """priorityフィルタが正しく動作することを確認する."""
    # Arrange
    repository = SQLAlchemyTodoRepository(repo_db_session)
    user_id = 1

    # Create todos with different priorities
    await repository.create(
        Todo.create(
            user_id=user_id,
            title="High Priority Todo",
            priority=TodoPriority.high,
        )
    )
    await repository.create(
        Todo.create(
            user_id=user_id,
            title="Low Priority Todo",
            priority=TodoPriority.low,
        )
    )

    # Act
    result = await repository.find_with_pagination(
        user_id=user_id, priority=TodoPriority.high
    )

    # Assert
    assert len(result) == 1
    assert result[0].priority == TodoPriority.high


async def test_find_with_pagination_success_returns_empty_list_when_no_todos(
    repo_db_session,
) -> None:
    """Todoが存在しない場合に空リストを返すことを確認する."""
    # Arrange
    repository = SQLAlchemyTodoRepository(repo_db_session)
    user_id = 999

    # Act
    result = await repository.find_with_pagination(user_id=user_id)

    # Assert
    assert result == []


async def test_find_with_pagination_success_filters_by_user_id(
    repo_db_session,
) -> None:
    """異なるユーザのTodoが返されないことを確認する."""
    # Arrange
    repository = SQLAlchemyTodoRepository(repo_db_session)
    user_id_1 = 1
    user_id_2 = 2

    # Create todos for different users
    await repository.create(
        Todo.create(
            user_id=user_id_1,
            title="User 1 Todo",
            priority=TodoPriority.medium,
        )
    )
    await repository.create(
        Todo.create(
            user_id=user_id_2,
            title="User 2 Todo",
            priority=TodoPriority.medium,
        )
    )

    # Act
    result = await repository.find_with_pagination(user_id=user_id_1)

    # Assert
    assert len(result) == 1
    assert result[0].user_id == user_id_1


async def test_find_with_pagination_failure_sqlalchemy_error_raises_data_operation_exception(  # noqa: E501
    repo_db_session_execute_sqlalchemy_error,
) -> None:
    """SQLAlchemyError発生時にDataOperationExceptionへラップされることを確認する."""
    # Arrange
    repository = SQLAlchemyTodoRepository(repo_db_session_execute_sqlalchemy_error)
    user_id = 1

    # Act / Assert
    with pytest.raises(DataOperationException) as exc_info:
        await repository.find_with_pagination(user_id=user_id)

    assert (
        exc_info.value.details.get("operation_context")
        == "SQLAlchemyTodoRepository.find_with_pagination"
    )
