"""CreateTodoUseCase正常系のテスト"""

from datetime import datetime
from unittest.mock import Mock

import pytest

from app.domain.entities.todo import Todo, TodoPriority
from app.domain.repositories.todo_repository import TodoRepository
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.transaction_manager import TransactionManager
from app.usecases.todo.create_todo_usecase import CreateTodoUseCase

pytestmark = pytest.mark.anyio("asyncio")


class _AsyncNoopTransactionContext:
    async def __aenter__(self):
        return None

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.fixture
def mock_transaction_manager() -> Mock:
    transaction_manager = Mock(spec=TransactionManager)
    transaction_manager.begin_transaction.return_value = _AsyncNoopTransactionContext()
    return transaction_manager


async def test_create_todo_success(mock_transaction_manager: Mock) -> None:
    todo_repository = Mock(spec=TodoRepository)
    user_repository = Mock(spec=UserRepository)

    user_repository.exists.return_value = True

    saved_todo = Todo(
        id=123,
        user_id=1,
        title="Write tests",
        description="Add unit test for todo creation",
        priority=TodoPriority.high,
    )
    todo_repository.save.return_value = saved_todo

    usecase = CreateTodoUseCase(
        transaction_manager=mock_transaction_manager,
        todo_repository=todo_repository,
        user_repository=user_repository,
    )

    due_date = datetime.utcnow()

    result = await usecase.execute(
        title="Write tests",
        user_id=1,
        description="Add unit test for todo creation",
        due_date=due_date,
        priority=TodoPriority.high,
    )

    assert result is saved_todo

    user_repository.exists.assert_awaited_once_with(1)
    todo_repository.save.assert_awaited_once()

    saved_arg = todo_repository.save.call_args.args[0]
    assert saved_arg.title == "Write tests"
    assert saved_arg.user_id == 1
    assert saved_arg.description == "Add unit test for todo creation"
    assert saved_arg.due_date == due_date
    assert saved_arg.priority == TodoPriority.high

    mock_transaction_manager.begin_transaction.assert_called_once()
