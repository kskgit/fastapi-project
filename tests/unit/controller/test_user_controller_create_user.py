from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.controller.dto.user_dto import UserCreateDTO, UserResponseDTO
from app.controller.user_controller import create_user
from app.domain.entities.user import User, UserRole
from app.usecases.user.create_user_usecase import CreateUserUseCase
from tests.unit.controller.exception_cases import (
    ControllerExceptionCase,
    controller_domain_exception_cases,
)


@pytest.mark.asyncio
async def test_create_user_success_returns_response() -> None:
    """create_userがユースケース呼び出しとレスポンス変換を行う正常系."""
    # Arrange
    request_dto = UserCreateDTO(
        username="viewer_user",
        email="viewer@example.com",
        full_name="Viewer User",
        role=UserRole.VIEWER,
    )
    returned_user = User(
        id=101,
        username=request_dto.username,
        email=request_dto.email,
        full_name=request_dto.full_name,
        is_active=True,
        created_at=datetime(2024, 12, 1, 10, 0, tzinfo=UTC),
        updated_at=datetime(2024, 12, 1, 10, 0, tzinfo=UTC),
    )

    usecase = AsyncMock(spec=CreateUserUseCase)
    usecase.execute.return_value = returned_user

    # Act
    response = await create_user(user_data=request_dto, usecase=usecase)

    # Assert
    usecase.execute.assert_awaited_once_with(
        username=request_dto.username,
        email=request_dto.email,
        full_name=request_dto.full_name,
        role=UserRole.VIEWER,
    )
    assert isinstance(response, UserResponseDTO)
    assert response.id == returned_user.id
    assert response.username == returned_user.username
    assert response.email == returned_user.email
    assert response.full_name == returned_user.full_name
    assert response.is_active is True
    assert response.role == UserRole.VIEWER
    assert response.created_at == returned_user.created_at
    assert response.updated_at == returned_user.updated_at


EXCEPTION_CASES = tuple[ControllerExceptionCase, ...](
    controller_domain_exception_cases()
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception_case",
    EXCEPTION_CASES,
    ids=[case.id for case in EXCEPTION_CASES],
)
async def test_create_user_propagates_domain_exceptions(
    exception_case: ControllerExceptionCase,
) -> None:
    """想定するドメイン例外は握り潰さずFastAPIのハンドラへ伝播する."""
    # Arrange
    request_dto = UserCreateDTO(
        username="viewer_user",
        email="viewer@example.com",
        full_name="Viewer User",
        role=UserRole.VIEWER,
    )
    usecase = AsyncMock(spec=CreateUserUseCase)
    raised_exception = exception_case.factory()
    usecase.execute.side_effect = raised_exception

    # Act / Assert
    with pytest.raises(type(raised_exception)) as exc_info:
        await create_user(user_data=request_dto, usecase=usecase)
    assert exc_info.value is raised_exception
