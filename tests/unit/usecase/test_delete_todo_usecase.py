"""DeleteTodoUseCase正常系のテスト"""

from unittest.mock import Mock

import pytest

from app.domain.entities import Todo
from app.domain.repositories import TodoRepository, UserRepository
from app.usecases.todo import DeleteTodoUseCase

pytestmark = pytest.mark.anyio("asyncio")


async def test_delete_todo_success(mock_transaction_manager: Mock) -> None:
    # Arrange
    todo_repository = Mock(spec=TodoRepository)
    user_repository = Mock(spec=UserRepository)

    todo_repository.find_by_id.return_value = Todo(
        id=99,
        user_id=5,
        title="テストTodo",
        description="削除用のTodo",
    )
    todo_repository.delete.return_value = True
    user_repository.exists.return_value = True

    usecase = DeleteTodoUseCase(
        transaction_manager=mock_transaction_manager,
        todo_repository=todo_repository,
        user_repository=user_repository,
    )

    # Act
    result = await usecase.execute(todo_id=99, user_id=5)

    # Assert
    assert result is True
    user_repository.exists.assert_awaited_once_with(5)
    todo_repository.find_by_id.assert_awaited_once_with(99)
    todo_repository.delete.assert_awaited_once_with(99)
    mock_transaction_manager.begin_transaction.assert_called_once()
