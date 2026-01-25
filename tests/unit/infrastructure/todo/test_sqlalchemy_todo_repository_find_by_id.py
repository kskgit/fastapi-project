"""Tests for SQLAlchemyTodoRepository.find_by_id."""

import pytest

from app.domain.entities import Todo, TodoPriority
from app.domain.exceptions import DataOperationException
from app.infrastructure.repositories import SQLAlchemyTodoRepository

pytestmark = pytest.mark.anyio("asyncio")


async def test_find_by_id_success_returns_todo(repo_db_session) -> None:
    """Todoが存在する場合にTodoエンティティを返すことを確認する."""
    # Arrange
    repository = SQLAlchemyTodoRepository(repo_db_session)
    saved = await repository.create(
        Todo.create(
            user_id=1,
            title="Test Todo",
            description="Test Description",
            priority=TodoPriority.high,
        )
    )
    assert saved.id is not None

    # Act
    result = await repository.find_by_id(saved.id)

    # Assert
    assert result is not None
    assert isinstance(result, Todo)
    assert result.id == saved.id
    assert result.title == "Test Todo"
    assert result.description == "Test Description"
    assert result.user_id == 1
    assert result.priority == TodoPriority.high


async def test_find_by_id_success_returns_none_when_not_found(
    repo_db_session,
) -> None:
    """Todoが存在しない場合にNoneを返すことを確認する."""
    # Arrange
    repository = SQLAlchemyTodoRepository(repo_db_session)

    # Act
    result = await repository.find_by_id(999)

    # Assert
    assert result is None


async def test_find_by_id_failure_sqlalchemy_error_raises_data_operation_exception(
    repo_db_session_execute_sqlalchemy_error,
) -> None:
    """SQLAlchemyError発生時にDataOperationExceptionへラップされることを確認する."""
    # Arrange
    repository = SQLAlchemyTodoRepository(repo_db_session_execute_sqlalchemy_error)

    # Act / Assert
    with pytest.raises(DataOperationException) as exc_info:
        await repository.find_by_id(1)

    assert (
        exc_info.value.details.get("operation_context")
        == "SQLAlchemyTodoRepository.find_by_id"
    )
