"""UpdateTodoUseCase正常系のテスト"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

from app.domain.entities.todo import Todo, TodoPriority, TodoStatus
from app.domain.repositories.todo_repository import TodoRepository
from app.domain.repositories.user_repository import UserRepository
from app.usecases.todo.update_todo_usecase import UpdateTodoUseCase


async def test_update_todo_success(mock_transaction_manager: Mock) -> None:
    # Arrange
    todo_repository = AsyncMock(spec=TodoRepository)
    user_repository = AsyncMock(spec=UserRepository)

    existing = Todo(
        id=1,
        user_id=1,
        title="Original title",
        description="Original description",
        due_date=datetime(2025, 1, 1, tzinfo=UTC),
        status=TodoStatus.pending,
        priority=TodoPriority.medium,
    )

    user_repository.exists.return_value = True
    todo_repository.find_by_id.return_value = existing
    todo_repository.update.side_effect = lambda todo: todo

    usecase = UpdateTodoUseCase(
        transaction_manager=mock_transaction_manager,
        todo_repository=todo_repository,
        user_repository=user_repository,
    )

    new_title = "Updated title"
    new_description = "Updated description"
    new_due_date = datetime(2025, 6, 1, tzinfo=UTC)
    new_status = TodoStatus.completed
    new_priority = TodoPriority.high

    # Act
    updated = await usecase.execute(
        todo_id=existing.id or -1,
        user_id=existing.user_id,
        title=new_title,
        description=new_description,
        due_date=new_due_date,
        status=new_status,
        priority=new_priority,
    )

    # Assert
    mock_transaction_manager.begin_transaction.assert_called_once()
    user_repository.exists.assert_awaited_once_with(existing.user_id)
    todo_repository.find_by_id.assert_awaited_once_with(existing.id)
    todo_repository.update.assert_awaited_once_with(existing)

    assert updated is existing
    assert updated.title == new_title
    assert updated.description == new_description
    assert updated.due_date == new_due_date
    assert updated.status == new_status
    assert updated.priority == new_priority
