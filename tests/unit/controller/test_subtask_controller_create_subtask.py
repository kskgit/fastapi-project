from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.controller.dto.subtask_dto import CreateSubTaskDTO, SubtaskResponseDTO
from app.controller.subtask_controller import create_subtask
from app.usecases.subtask.create_subtask_usecase import CreateSubTaskUseCase


@pytest.mark.asyncio
async def test_create_subtask_success() -> None:
    # Arrange
    userId = 1
    request_dto = CreateSubTaskDTO(user_id=userId, title="タイトル")
    returned_subtask = SubtaskResponseDTO(
        id=1,
        todo_id=1,
        user_id=userId,
        title="タイトル",
        due_date=datetime(2024, 1, 10, tzinfo=UTC),
        is_completed=False,
        completed_at=None,
        created_at=datetime(2024, 1, 10, tzinfo=UTC),
        updated_at=datetime(2024, 1, 10, tzinfo=UTC),
    )

    usecase = AsyncMock(spec=CreateSubTaskUseCase)
    usecase.execute.return_value = returned_subtask

    # Act
    await create_subtask(request=request_dto, usecase=usecase)

    # Assert
    usecase.execute.assert_awaited_once_with()
