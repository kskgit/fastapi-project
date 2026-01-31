"""GetTodoByIdUseCase のテスト."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.domain.entities import SubTask, Todo, TodoPriority, TodoStatus
from app.domain.exceptions import TodoNotFoundException, UserNotFoundException
from app.domain.repositories import SubTaskRepository, TodoRepository, UserRepository
from app.usecases.todo import GetTodoByIdUseCase

pytestmark = pytest.mark.anyio("asyncio")


def _sample_todo(todo_id: int, user_id: int) -> Todo:
    timestamp = datetime(2024, 1, 1, tzinfo=UTC)
    return Todo(
        id=todo_id,
        user_id=user_id,
        title="Test Todo",
        description=None,
        due_date=timestamp,
        status=TodoStatus.pending,
        priority=TodoPriority.medium,
        created_at=timestamp,
        updated_at=timestamp,
    )


def _sample_subtask(subtask_id: int, todo_id: int, user_id: int, title: str) -> SubTask:
    timestamp = datetime(2024, 1, 1, tzinfo=UTC)
    return SubTask(
        id=subtask_id,
        todo_id=todo_id,
        user_id=user_id,
        title=title,
        is_compleated=False,
        created_at=timestamp,
        updated_at=timestamp,
    )


async def test_get_todo_by_id_success_with_subtasks() -> None:
    """Todoとその紐づくサブタスクが取得できる."""
    # Arrange
    todo_repository = AsyncMock(spec=TodoRepository)
    user_repository = AsyncMock(spec=UserRepository)
    subtask_repository = AsyncMock(spec=SubTaskRepository)

    user_repository.exists.return_value = True
    todo = _sample_todo(todo_id=1, user_id=5)
    todo_repository.find_by_id.return_value = todo

    subtasks = [
        _sample_subtask(subtask_id=10, todo_id=1, user_id=5, title="Subtask 1"),
        _sample_subtask(subtask_id=11, todo_id=1, user_id=5, title="Subtask 2"),
    ]
    subtask_repository.find_by_todo_id.return_value = subtasks

    usecase = GetTodoByIdUseCase(
        todo_repository=todo_repository,
        user_repository=user_repository,
        subtask_repository=subtask_repository,
    )

    # Act
    result = await usecase.execute(todo_id=1, user_id=5)

    # Assert
    todo_repository.find_by_id.assert_awaited_once_with(1)
    subtask_repository.find_by_todo_id.assert_awaited_once_with(1)
    assert result.todo == todo
    assert result.subtasks == subtasks


async def test_get_todo_by_id_success_without_subtasks() -> None:
    """サブタスクがないTodoも正常に取得できる."""
    # Arrange
    todo_repository = AsyncMock(spec=TodoRepository)
    user_repository = AsyncMock(spec=UserRepository)
    subtask_repository = AsyncMock(spec=SubTaskRepository)

    user_repository.exists.return_value = True
    todo = _sample_todo(todo_id=1, user_id=5)
    todo_repository.find_by_id.return_value = todo
    subtask_repository.find_by_todo_id.return_value = []

    usecase = GetTodoByIdUseCase(
        todo_repository=todo_repository,
        user_repository=user_repository,
        subtask_repository=subtask_repository,
    )

    # Act
    result = await usecase.execute(todo_id=1, user_id=5)

    # Assert
    todo_repository.find_by_id.assert_awaited_once_with(1)
    subtask_repository.find_by_todo_id.assert_awaited_once_with(1)
    assert result.todo == todo
    assert result.subtasks == []


async def test_get_todo_by_id_failure_todo_not_found() -> None:
    """Todoが存在しない場合はTodoNotFoundException."""
    # Arrange
    todo_repository = AsyncMock(spec=TodoRepository)
    user_repository = AsyncMock(spec=UserRepository)
    subtask_repository = AsyncMock(spec=SubTaskRepository)

    todo_repository.find_by_id.return_value = None

    usecase = GetTodoByIdUseCase(
        todo_repository=todo_repository,
        user_repository=user_repository,
        subtask_repository=subtask_repository,
    )

    # Act / Assert
    with pytest.raises(TodoNotFoundException):
        await usecase.execute(todo_id=999, user_id=5)

    subtask_repository.find_by_todo_id.assert_not_called()


async def test_get_todo_by_id_failure_user_not_found() -> None:
    """ユーザーが存在しない場合はUserNotFoundException."""
    # Arrange
    todo_repository = AsyncMock(spec=TodoRepository)
    user_repository = AsyncMock(spec=UserRepository)
    subtask_repository = AsyncMock(spec=SubTaskRepository)

    todo = _sample_todo(todo_id=1, user_id=5)
    todo_repository.find_by_id.return_value = todo
    user_repository.exists.return_value = False

    usecase = GetTodoByIdUseCase(
        todo_repository=todo_repository,
        user_repository=user_repository,
        subtask_repository=subtask_repository,
    )

    # Act / Assert
    with pytest.raises(UserNotFoundException):
        await usecase.execute(todo_id=1, user_id=5)

    subtask_repository.find_by_todo_id.assert_not_called()


async def test_get_todo_by_id_failure_ownership_mismatch() -> None:
    """他ユーザーのTodoはTodoNotFoundException."""
    # Arrange
    todo_repository = AsyncMock(spec=TodoRepository)
    user_repository = AsyncMock(spec=UserRepository)
    subtask_repository = AsyncMock(spec=SubTaskRepository)

    # Todo belongs to user 5, but user 10 is trying to access
    todo = _sample_todo(todo_id=1, user_id=5)
    todo_repository.find_by_id.return_value = todo
    user_repository.exists.return_value = True

    usecase = GetTodoByIdUseCase(
        todo_repository=todo_repository,
        user_repository=user_repository,
        subtask_repository=subtask_repository,
    )

    # Act / Assert
    with pytest.raises(TodoNotFoundException):
        await usecase.execute(todo_id=1, user_id=10)

    subtask_repository.find_by_todo_id.assert_not_called()
