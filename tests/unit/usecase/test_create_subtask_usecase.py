from unittest.mock import AsyncMock, Mock

from app.domain.repositories import SubTaskRepository, TodoRepository, UserRepository
from app.domain.services import SubTaskDomainService
from app.domain.subtask import SubTask
from app.usecases.subtask import CreateSubTaskUseCase


async def test_create_subtask_success(mock_transaction_manager: Mock) -> None:
    # Arrange
    mock_user_repository = AsyncMock(spec=UserRepository)
    mock_todo_repository = AsyncMock(spec=TodoRepository)
    mock_subtask_repository = AsyncMock(spec=SubTaskRepository)
    mock_subtask_domain_service = AsyncMock(spec=SubTaskDomainService)

    usecase = CreateSubTaskUseCase(
        transaction_manager=mock_transaction_manager,
        user_repository=mock_user_repository,
        todo_repository=mock_todo_repository,
        subtask_repository=mock_subtask_repository,
        subtask_domain_service=mock_subtask_domain_service,
    )

    user_id = 1
    todo_id = 2

    expected_subtask = SubTask(
        user_id=user_id,
        todo_id=todo_id,
        title="Title",
        is_compleated=False,
    )
    mock_subtask_repository.create.return_value = expected_subtask

    # Act
    result = await usecase.execute(
        user_id=user_id,
        todo_id=todo_id,
        title="Title",
    )

    # Assert
    mock_transaction_manager.begin_transaction.assert_called_once()
    mock_subtask_domain_service.ensure_todo_user_can_modify_subtask.assert_awaited_once_with(
        user_id=user_id,
        todo_id=todo_id,
        user_repository=mock_user_repository,
        todo_repository=mock_todo_repository,
    )
    mock_subtask_repository.create.assert_awaited_once()

    assert result == expected_subtask
