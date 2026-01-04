from unittest.mock import AsyncMock

from app.domain.entities.todo import Todo, TodoPriority
from app.domain.entities.user import User, UserRole
from app.domain.repositories.todo_repository import TodoRepository
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.subtask_domain_service import SubTaskDomainService


async def test_ensure_todo_user_can_modify_subtask_success() -> None:
    # Arrange
    subtask_domain_service = SubTaskDomainService()

    user_id = 1
    mock_user_repository = AsyncMock(spec=UserRepository)
    # TODO 引数を指定する
    mock_user_repository.find_by_id.return_value = User(
        id=1,
        username="member_user",
        email="taken@example.com",
        role=UserRole.MEMBER,
    )

    todo_id = 2
    mock_todo_repository = AsyncMock(spec=TodoRepository)
    # TODO 引数を指定する
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
