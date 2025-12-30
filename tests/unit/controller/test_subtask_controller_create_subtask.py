from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.controller.dto.subtask_dto import CreateSubTaskDTO, SubtaskResponseDTO
from app.controller.subtask_controller import create_subtask
from app.usecases.subtask.create_subtask_usecase import CreateSubTaskUseCase


@pytest.mark.asyncio
async def test_create_subtask_success() -> None:
    # Arrange
    user_id = 1
    todo_id = 2
    title = "タイトル"

    request_dto = CreateSubTaskDTO(
        user_id=user_id,
        title=title,
    )

    returned_subtask = SubtaskResponseDTO(
        id=1,
        todo_id=todo_id,
        user_id=user_id,
        title=title,
        due_date=datetime(2024, 1, 10, tzinfo=UTC),
        is_completed=False,
        completed_at=None,
        created_at=datetime(2024, 1, 10, tzinfo=UTC),
        updated_at=datetime(2024, 1, 10, tzinfo=UTC),
    )

    usecase = AsyncMock(spec=CreateSubTaskUseCase)
    usecase.execute.return_value = returned_subtask

    # Act
    res = await create_subtask(todo_id=todo_id, request=request_dto, usecase=usecase)

    # Assert
    usecase.execute.assert_awaited_once_with(
        user_id=request_dto.user_id,
        todo_id=todo_id,
        title=request_dto.title,
    )

    assert res.id is not None
    assert res.todo_id == todo_id
    assert res.user_id == request_dto.user_id
    assert res.title == request_dto.title
    assert res.due_date is None
    assert not res.is_completed
    assert res.completed_at is None
    assert res.created_at is not None
    assert res.updated_at is not None
