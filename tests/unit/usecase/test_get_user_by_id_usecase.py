"""GetUserByIdUseCase のユニットテスト."""

from unittest.mock import AsyncMock

import pytest

from app.domain.entities.user import User
from app.domain.exceptions import UserNotFoundException
from app.domain.repositories.user_repository import UserRepository
from app.usecases.user.get_user_by_id_usecase import GetUserByIdUseCase

pytestmark = pytest.mark.anyio("asyncio")


async def test_get_user_by_id_success() -> None:
    """指定した ID のユーザーが取得できることを確認する."""
    # Arrange
    user_id = 1
    expected_user = User(
        id=user_id,
        username="tester",
        email="tester@example.com",
    )

    user_repository = AsyncMock(spec=UserRepository)
    user_repository.find_by_id.return_value = expected_user

    usecase = GetUserByIdUseCase(user_repository=user_repository)

    # Act
    result = await usecase.execute(user_id=user_id)

    # Assert
    user_repository.find_by_id.assert_awaited_once_with(user_id)
    assert result is expected_user


async def test_get_user_by_id_failure_user_not_found() -> None:
    """存在しない ID を指定した場合に UserNotFoundException となることを確認する."""
    # Arrange
    user_id = 999
    user_repository = AsyncMock(spec=UserRepository)
    user_repository.find_by_id.return_value = None

    usecase = GetUserByIdUseCase(user_repository=user_repository)

    # Act / Assert
    with pytest.raises(UserNotFoundException):
        await usecase.execute(user_id=user_id)

    user_repository.find_by_id.assert_awaited_once_with(user_id)
