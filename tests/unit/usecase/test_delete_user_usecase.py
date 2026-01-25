"""DeleteUserUseCaseのユニットテスト"""

from unittest.mock import AsyncMock, Mock

import pytest

from app.domain.entities import User
from app.domain.repositories import TodoRepository, UserRepository
from app.usecases.user import DeleteUserUseCase

pytestmark = pytest.mark.anyio("asyncio")


async def test_delete_user_success(mock_transaction_manager: Mock) -> None:
    # Arrange
    user_id = 1

    user_repository = AsyncMock(spec=UserRepository)
    existing_user = User(username="tester", email="tester@example.com", id=user_id)
    user_repository.find_by_id.return_value = existing_user
    user_repository.delete.return_value = True

    todo_repository = AsyncMock(spec=TodoRepository)

    usecase = DeleteUserUseCase(
        transaction_manager=mock_transaction_manager,
        user_repository=user_repository,
        todo_repository=todo_repository,
    )

    # Act
    result = await usecase.execute(user_id)

    # Assert
    assert result is True

    mock_transaction_manager.begin_transaction.assert_called_once()
    user_repository.find_by_id.assert_awaited_once_with(user_id)
    todo_repository.delete_all_by_user_id.assert_awaited_once_with(user_id)
    user_repository.delete.assert_awaited_once_with(user_id)


async def test_delete_user_failure_user_not_found(
    mock_transaction_manager: Mock,
) -> None:
    # Arrange
    user_repository = AsyncMock(spec=UserRepository)
    user_repository.find_by_id.return_value = None

    todo_repository = AsyncMock(spec=TodoRepository)

    usecase = DeleteUserUseCase(
        transaction_manager=mock_transaction_manager,
        user_repository=user_repository,
        todo_repository=todo_repository,
    )

    # Act
    result = await usecase.execute(999)

    # Assert
    assert result is False
    mock_transaction_manager.begin_transaction.assert_called_once()
    user_repository.find_by_id.assert_awaited_once_with(999)
    todo_repository.delete_all_by_user_id.assert_not_called()
    user_repository.delete.assert_not_called()


async def test_delete_user_failure_todo_delete_error(
    mock_transaction_manager: Mock,
) -> None:
    # Arrange
    user_repository = AsyncMock(spec=UserRepository)
    todo_repository = AsyncMock(spec=TodoRepository)

    existing_user = User(username="tester", email="tester@example.com", id=20)
    user_repository.find_by_id.return_value = existing_user
    todo_delete_error = RuntimeError("todo delete failed")
    todo_repository.delete_all_by_user_id.side_effect = todo_delete_error

    usecase = DeleteUserUseCase(
        transaction_manager=mock_transaction_manager,
        user_repository=user_repository,
        todo_repository=todo_repository,
    )

    # Act & Assert
    with pytest.raises(RuntimeError) as exc_info:
        await usecase.execute(20)

    assert exc_info.value is todo_delete_error

    mock_transaction_manager.begin_transaction.assert_called_once()
    user_repository.find_by_id.assert_awaited_once_with(20)
    todo_repository.delete_all_by_user_id.assert_awaited_once_with(20)
    user_repository.delete.assert_not_called()


async def test_delete_user_failure_user_delete_returns_false(
    mock_transaction_manager: Mock,
) -> None:
    # Arrange
    user_repository = AsyncMock(spec=UserRepository)
    existing_user = User(username="tester", email="tester@example.com", id=10)
    user_repository.find_by_id.return_value = existing_user
    user_repository.delete.return_value = False

    todo_repository = AsyncMock(spec=TodoRepository)

    usecase = DeleteUserUseCase(
        transaction_manager=mock_transaction_manager,
        user_repository=user_repository,
        todo_repository=todo_repository,
    )

    # Act & Assert
    with pytest.raises(RuntimeError, match="Failed to delete user with id 10"):
        await usecase.execute(10)

    mock_transaction_manager.begin_transaction.assert_called_once()
    user_repository.find_by_id.assert_awaited_once_with(10)
    todo_repository.delete_all_by_user_id.assert_awaited_once_with(10)
    user_repository.delete.assert_awaited_once_with(10)
