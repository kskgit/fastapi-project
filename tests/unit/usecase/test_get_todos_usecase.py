"""GetTodosUseCase のテスト."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.domain.entities.todo import Todo, TodoPriority, TodoStatus
from app.domain.exceptions import UserNotFoundException, ValidationException
from app.domain.repositories.todo_repository import TodoRepository
from app.domain.repositories.user_repository import UserRepository
from app.usecases.todo.get_todos_usecase import GetTodosUseCase

pytestmark = pytest.mark.anyio("asyncio")


def _sample_todo(todo_id: int, user_id: int) -> Todo:
    timestamp = datetime(2024, 1, 1, tzinfo=UTC)
    return Todo(
        id=todo_id,
        user_id=user_id,
        title="Task",
        description=None,
        due_date=timestamp,
        status=TodoStatus.pending,
        priority=TodoPriority.medium,
        created_at=timestamp,
        updated_at=timestamp,
    )


async def test_get_todos_success_with_filters() -> None:
    """ユーザーのTodo一覧がフィルタ付きで取得できる."""
    # Arrange
    todo_repository = AsyncMock(spec=TodoRepository)
    user_repository = AsyncMock(spec=UserRepository)
    user_repository.exists.return_value = True
    todos = [_sample_todo(todo_id=1, user_id=5), _sample_todo(todo_id=2, user_id=5)]
    todo_repository.find_with_pagination.return_value = todos
    usecase = GetTodosUseCase(
        todo_repository=todo_repository,
        user_repository=user_repository,
    )

    # Act
    result = await usecase.execute(
        user_id=5,
        skip=10,
        limit=20,
        status=TodoStatus.in_progress,
        priority=TodoPriority.high,
    )

    # Assert
    user_repository.exists.assert_awaited_once_with(5)
    todo_repository.find_with_pagination.assert_awaited_once_with(
        user_id=5,
        skip=10,
        limit=20,
        status=TodoStatus.in_progress,
        priority=TodoPriority.high,
    )
    assert result == todos


async def test_get_todos_failure_user_not_found() -> None:
    """ユーザーが存在しない場合はUserNotFoundException."""
    # Arrange
    todo_repository = AsyncMock(spec=TodoRepository)
    user_repository = AsyncMock(spec=UserRepository)
    user_repository.exists.return_value = False
    usecase = GetTodosUseCase(
        todo_repository=todo_repository,
        user_repository=user_repository,
    )

    # Act / Assert
    with pytest.raises(UserNotFoundException):
        await usecase.execute(user_id=1, skip=0, limit=10)
    todo_repository.find_with_pagination.assert_not_called()


async def test_get_todos_failure_limit_too_large() -> None:
    """limit超過の場合はValidationExceptionとなる."""
    # Arrange
    todo_repository = AsyncMock(spec=TodoRepository)
    user_repository = AsyncMock(spec=UserRepository)
    user_repository.exists.return_value = True
    usecase = GetTodosUseCase(
        todo_repository=todo_repository,
        user_repository=user_repository,
    )

    # Act / Assert
    with pytest.raises(ValidationException):
        await usecase.execute(user_id=1, skip=0, limit=1001)
    todo_repository.find_with_pagination.assert_not_called()


async def test_get_todos_failure_negative_skip() -> None:
    """skipが負の場合もValidationException."""
    # Arrange
    todo_repository = AsyncMock(spec=TodoRepository)
    user_repository = AsyncMock(spec=UserRepository)
    user_repository.exists.return_value = True
    usecase = GetTodosUseCase(
        todo_repository=todo_repository,
        user_repository=user_repository,
    )

    # Act / Assert
    with pytest.raises(ValidationException):
        await usecase.execute(user_id=1, skip=-1, limit=10)
    todo_repository.find_with_pagination.assert_not_called()
