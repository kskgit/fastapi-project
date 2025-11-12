from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.controller.dto.todo_dto import CreateTodoDTO, TodoResponseDTO
from app.controller.todo_controller import create_todo
from app.domain.entities.todo import Todo, TodoPriority, TodoStatus
from app.usecases.todo.create_todo_usecase import CreateTodoUseCase
from tests.unit.controller.exception_cases import (
    ControllerExceptionCase,
    controller_domain_exception_cases,
)


@pytest.mark.asyncio
async def test_create_todo_success_returns_response() -> None:
    """create_todoがユースケース呼び出しとレスポンス変換を行う正常系."""
    # Arrange
    request_dto = CreateTodoDTO(
        user_id=1,
        title="Write release note",
        description="Summarize changes",
        due_date=datetime(2024, 12, 31, 15, 0, tzinfo=UTC),
        priority=TodoPriority.high,
    )
    returned_todo = Todo(
        id=42,
        title=request_dto.title,
        description=request_dto.description,
        due_date=request_dto.due_date,
        priority=request_dto.priority,
        status=TodoStatus.pending,
        user_id=request_dto.user_id,
        created_at=datetime(2024, 12, 1, 10, 0, tzinfo=UTC),
        updated_at=datetime(2024, 12, 1, 10, 0, tzinfo=UTC),
    )
    usecase = AsyncMock(spec=CreateTodoUseCase)
    usecase.execute.return_value = returned_todo

    # Act
    response = await create_todo(todo_data=request_dto, usecase=usecase)

    # Assert
    usecase.execute.assert_awaited_once_with(
        title=request_dto.title,
        user_id=request_dto.user_id,
        description=request_dto.description,
        due_date=request_dto.due_date,
        priority=request_dto.priority,
    )
    assert isinstance(response, TodoResponseDTO)
    assert response.id == returned_todo.id
    assert response.title == returned_todo.title
    assert response.description == returned_todo.description
    assert response.priority == returned_todo.priority
    assert response.due_date == returned_todo.due_date
    assert response.status == returned_todo.status
    assert response.created_at == returned_todo.created_at
    assert response.updated_at == returned_todo.updated_at


EXCEPTION_CASES = tuple[ControllerExceptionCase, ...](
    controller_domain_exception_cases()
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception_case",
    EXCEPTION_CASES,
    ids=[case.id for case in EXCEPTION_CASES],
)
async def test_create_todo_propagates_domain_exceptions(
    exception_case: ControllerExceptionCase,
) -> None:
    """想定するドメイン例外は握り潰さずFastAPIのハンドラへ伝播する."""
    # Arrange
    request_dto = CreateTodoDTO(
        user_id=1,
        title="Valid title",
        description="",
        due_date=None,
        priority=TodoPriority.medium,
    )
    usecase = AsyncMock(spec=CreateTodoUseCase)
    raised_exception = exception_case.factory()
    usecase.execute.side_effect = raised_exception

    # Act / Assert
    with pytest.raises(type(raised_exception)) as exc_info:
        await create_todo(todo_data=request_dto, usecase=usecase)
    assert exc_info.value is raised_exception
