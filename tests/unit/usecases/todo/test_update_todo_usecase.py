from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest

from app.core.transaction_manager import TransactionManager
from app.domain.entities.todo import Todo, TodoPriority, TodoStatus
from app.domain.repositories.todo_repository import TodoRepository
from app.domain.repositories.user_repository import UserRepository
from app.usecases.todo.update_todo_usecase import UpdateTodoUseCase

# pytest-asyncio v0.17.0以降、@pytest.mark.asyncioは不要


@pytest.fixture
def mock_transaction_manager() -> AsyncMock:
    """Fixture for a mocked transaction manager."""
    mock = AsyncMock(spec=TransactionManager)
    mock.begin_transaction.return_value.__aenter__.return_value = None
    mock.begin_transaction.return_value.__aexit__.return_value = None
    return mock


@pytest.fixture
def mock_todo_repository() -> AsyncMock:
    """Fixture for a mocked todo repository."""
    return AsyncMock(spec=TodoRepository)


@pytest.fixture
def mock_user_repository() -> AsyncMock:
    """Fixture for a mocked user repository."""
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def update_todo_usecase(
    mock_transaction_manager: AsyncMock,
    mock_todo_repository: AsyncMock,
    mock_user_repository: AsyncMock,
) -> UpdateTodoUseCase:
    """Fixture for the UpdateTodoUseCase."""
    return UpdateTodoUseCase(
        transaction_manager=mock_transaction_manager,
        todo_repository=mock_todo_repository,
        user_repository=mock_user_repository,
    )


@pytest.fixture
def existing_todo() -> Todo:
    """Fixture for an existing Todo entity."""
    current_time = datetime.now(UTC)
    return Todo(
        id=1,
        user_id=1,
        title="Original Title",
        description="Original Description",
        due_date=datetime(2025, 12, 31, 10, 0, 0, tzinfo=UTC),
        status=TodoStatus.in_progress,
        priority=TodoPriority.medium,
        created_at=current_time,
        updated_at=current_time,
    )


@pytest.mark.unit
async def test_update_todo_success(
    update_todo_usecase: UpdateTodoUseCase,
    mock_user_repository: AsyncMock,
    mock_todo_repository: AsyncMock,
    existing_todo: Todo,
):
    """
    正常系テスト:
    指定されたフィールドを更新し、更新されたTodoエンティティを返すことを確認する。
    """
    # Arrange
    user_id = 1
    todo_id = 1
    new_title = "Updated Title"
    new_status = TodoStatus.completed
    new_priority = TodoPriority.high
    new_description = "Updated description."
    new_due_date = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)

    mock_user_repository.exists.return_value = True
    mock_todo_repository.find_by_id.return_value = existing_todo
    mock_todo_repository.update.side_effect = lambda todo: todo

    # Act
    with patch.object(Todo, "update", new_callable=AsyncMock) as mock_todo_update:
        updated_todo = await update_todo_usecase.execute(
            todo_id=todo_id,
            user_id=user_id,
            title=new_title,
            description=new_description,
            due_date=new_due_date,
            status=new_status,
            priority=new_priority,
        )

    # Assert
    mock_user_repository.exists.assert_awaited_once_with(user_id)
    mock_todo_repository.find_by_id.assert_awaited_once_with(todo_id)

    mock_todo_update.assert_awaited_once_with(
        user_id,
        mock_user_repository,
        update_todo_usecase.todo_domain_service,
        new_title,
        new_description,
        new_due_date,
        new_status,
        new_priority,
    )

    mock_todo_repository.update.assert_awaited_once_with(existing_todo)

    assert updated_todo is existing_todo
