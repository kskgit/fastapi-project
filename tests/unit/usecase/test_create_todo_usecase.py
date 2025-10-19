"""CreateTodoUseCase正常系のテスト"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from app.domain.entities.todo import Todo, TodoPriority
from app.domain.exceptions.business import UserNotFoundException
from app.domain.repositories.todo_repository import TodoRepository
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.user_domain_service import UserDomainService
from app.usecases.todo.create_todo_usecase import CreateTodoUseCase


async def test_create_todo_success(mock_transaction_manager: Mock) -> None:
    # Arrange
    todo_repository = AsyncMock(spec=TodoRepository)
    user_repository = AsyncMock(spec=UserRepository)
    user_domain_service = AsyncMock(spec=UserDomainService)

    saved_todo = Todo(
        id=123,
        user_id=1,
        title="Write tests",
        description="Add unit test for todo creation",
        priority=TodoPriority.high,
    )
    todo_repository.create.return_value = saved_todo

    usecase = CreateTodoUseCase(
        transaction_manager=mock_transaction_manager,
        todo_repository=todo_repository,
        user_repository=user_repository,
        user_domain_service=user_domain_service,
    )

    due_date = datetime.now(UTC)

    # Act
    result = await usecase.execute(
        title="Write tests",
        user_id=1,
        description="Add unit test for todo creation",
        due_date=due_date,
        priority=TodoPriority.high,
    )

    # Assert
    assert result is saved_todo

    user_domain_service.validate_user_exists.assert_awaited_once_with(
        1, user_repository=user_repository
    )
    todo_repository.create.assert_awaited_once()

    saved_arg = todo_repository.create.call_args.args[0]
    assert saved_arg.title == "Write tests"
    assert saved_arg.user_id == 1
    assert saved_arg.description == "Add unit test for todo creation"
    assert saved_arg.due_date == due_date
    assert saved_arg.priority == TodoPriority.high

    mock_transaction_manager.begin_transaction.assert_called_once()


async def test_create_todo_failure_user_not_found(
    mock_transaction_manager: Mock,
) -> None:
    # Arrange
    todo_repository = AsyncMock(spec=TodoRepository)
    user_repository = AsyncMock(spec=UserRepository)
    user_domain_service = AsyncMock(spec=UserDomainService)
    user_domain_service.validate_user_exists.side_effect = UserNotFoundException(999)

    usecase = CreateTodoUseCase(
        transaction_manager=mock_transaction_manager,
        todo_repository=todo_repository,
        user_repository=user_repository,
        user_domain_service=user_domain_service,
    )

    # Act & Assert
    with pytest.raises(UserNotFoundException):
        await usecase.execute(title="Write tests", user_id=999)

    user_domain_service.validate_user_exists.assert_awaited_once_with(
        999, user_repository=user_repository
    )
    todo_repository.create.assert_not_called()
    mock_transaction_manager.begin_transaction.assert_called_once()


async def test_create_todo_failure_save_error(
    mock_transaction_manager: Mock,
) -> None:
    # Arrange
    todo_repository = AsyncMock(spec=TodoRepository)
    user_repository = AsyncMock(spec=UserRepository)
    user_domain_service = AsyncMock(spec=UserDomainService)
    user_domain_service.validate_user_exists.return_value = None

    persistence_error = RuntimeError("failed to save todo")
    todo_repository.create.side_effect = persistence_error

    usecase = CreateTodoUseCase(
        transaction_manager=mock_transaction_manager,
        todo_repository=todo_repository,
        user_repository=user_repository,
        user_domain_service=user_domain_service,
    )

    # Act & Assert
    with pytest.raises(RuntimeError) as exc_info:
        await usecase.execute(title="Write tests", user_id=1)

    assert exc_info.value is persistence_error

    user_domain_service.validate_user_exists.assert_awaited_once_with(
        1, user_repository=user_repository
    )
    todo_repository.create.assert_awaited_once()

    mock_transaction_manager.begin_transaction.assert_called_once()
