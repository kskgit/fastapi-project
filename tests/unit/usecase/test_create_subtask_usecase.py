from unittest.mock import Mock

from app.domain.subtask import SubTask
from app.usecases.subtask.create_subtask_usecase import CreateSubTaskUseCase


async def test_create_subtask_success(mock_transaction_manager: Mock) -> None:
    # Arrange
    usecase = CreateSubTaskUseCase(
        transaction_manager=mock_transaction_manager,
    )

    expected_subtask = SubTask(
        user_id=1,
        todo_id=2,
        title="Title",
        is_compleated=False,
    )

    # Act
    result = await usecase.execute(
        user_id=1,
        todo_id=2,
        title="Title",
    )
    mock_transaction_manager.begin_transaction.assert_called_once()

    assert result == expected_subtask
