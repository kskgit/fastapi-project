from unittest.mock import AsyncMock

import pytest

from app.domain.entities.todo import Todo, TodoPriority
from app.domain.entities.user import User, UserRole
from app.domain.exceptions import TodoNotFoundException, UserNotFoundException
from app.domain.repositories.todo_repository import TodoRepository
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.subtask_domain_service import SubTaskDomainService


async def test_ensure_todo_user_can_modify_subtask_success() -> None:
    # Arrange
    subtask_domain_service = SubTaskDomainService()

    user_id = 1
    mock_user_repository = AsyncMock(spec=UserRepository)
    mock_user_repository.find_by_id.return_value = User(
        id=1,
        username="member_user",
        email="taken@example.com",
        role=UserRole.MEMBER,
    )

    todo_id = 2
    mock_todo_repository = AsyncMock(spec=TodoRepository)
    mock_todo_repository.find_by_id.return_value = Todo.create(
        user_id=user_id,
        title="Todo",
        description="test todo",
        priority=TodoPriority.medium,
    )

    # Act
    result = await subtask_domain_service.ensure_todo_user_can_modify_subtask(
        user_id=user_id,
        todo_id=todo_id,
        user_repository=mock_user_repository,
        todo_repository=mock_todo_repository,
    )

    # Assert
    mock_user_repository.find_by_id.assert_awaited_once_with(user_id=user_id)
    mock_todo_repository.find_by_id.assert_awaited_once_with(todo_id=todo_id)
    assert result is True


async def test_ensure_todo_user_can_modify_subtask_failer_todo_not_found() -> None:
    # Arrange
    subtask_domain_service = SubTaskDomainService()

    user_id = 1
    mock_user_repository = AsyncMock(spec=UserRepository)
    mock_user_repository.find_by_id.return_value = User(
        id=1,
        username="member_user",
        email="taken@example.com",
        role=UserRole.MEMBER,
    )

    todo_id = 2
    mock_todo_repository = AsyncMock(spec=TodoRepository)
    mock_todo_repository.find_by_id.return_value = None

    # Act / Assert
    with pytest.raises(TodoNotFoundException):
        await subtask_domain_service.ensure_todo_user_can_modify_subtask(
            user_id=user_id,
            todo_id=todo_id,
            user_repository=mock_user_repository,
            todo_repository=mock_todo_repository,
        )

    mock_todo_repository.find_by_id.assert_awaited_once_with(todo_id=todo_id)
    mock_user_repository.find_by_id.assert_not_called()


async def test_ensure_todo_user_can_modify_subtask_failer_owner_mismatch() -> None:
    # Arrange
    subtask_domain_service = SubTaskDomainService()

    request_user_id = 1
    mock_user_repository = AsyncMock(spec=UserRepository)

    todo_id = 2
    mock_todo_repository = AsyncMock(spec=TodoRepository)
    mock_todo_repository.find_by_id.return_value = Todo.create(
        user_id=999,
        title="Todo",
        description="test todo",
        priority=TodoPriority.medium,
    )

    # Act / Assert
    with pytest.raises(TodoNotFoundException):
        await subtask_domain_service.ensure_todo_user_can_modify_subtask(
            user_id=request_user_id,
            todo_id=todo_id,
            user_repository=mock_user_repository,
            todo_repository=mock_todo_repository,
        )

    mock_todo_repository.find_by_id.assert_awaited_once_with(todo_id=todo_id)
    mock_user_repository.find_by_id.assert_not_called()


async def test_ensure_todo_user_can_modify_subtask_failer_user_not_found() -> None:
    # Arrange
    subtask_domain_service = SubTaskDomainService()

    user_id = 1
    mock_user_repository = AsyncMock(spec=UserRepository)
    mock_user_repository.find_by_id.return_value = None

    todo_id = 2
    mock_todo_repository = AsyncMock(spec=TodoRepository)
    mock_todo_repository.find_by_id.return_value = Todo.create(
        user_id=user_id,
        title="Todo",
        description="test todo",
        priority=TodoPriority.medium,
    )

    # Act / Assert
    with pytest.raises(UserNotFoundException):
        await subtask_domain_service.ensure_todo_user_can_modify_subtask(
            user_id=user_id,
            todo_id=todo_id,
            user_repository=mock_user_repository,
            todo_repository=mock_todo_repository,
        )

    mock_user_repository.find_by_id.assert_awaited_once_with(user_id=user_id)
    mock_todo_repository.find_by_id.assert_awaited_once_with(todo_id=todo_id)
