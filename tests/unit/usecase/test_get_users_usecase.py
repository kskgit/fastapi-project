"""GetUsersUseCase のユニットテスト."""

from unittest.mock import AsyncMock, Mock

import pytest

from app.domain.entities import User
from app.domain.exceptions import ValidationException
from app.domain.repositories import UserRepository
from app.domain.services import UserDomainService
from app.usecases.user import GetUsersUseCase

pytestmark = pytest.mark.anyio("asyncio")


async def test_get_users_success() -> None:
    """ユーザーリストが正しく取得できることを確認する."""
    # Arrange
    expected_users = [
        User(id=1, username="user1", email="user1@example.com"),
        User(id=2, username="user2", email="user2@example.com"),
        User(id=3, username="user3", email="user3@example.com"),
    ]

    user_repository = AsyncMock(spec=UserRepository)
    user_repository.find_all.return_value = expected_users

    usecase = GetUsersUseCase(user_repository=user_repository)
    user_domain_service = Mock(spec=UserDomainService)
    usecase.user_domain_service = user_domain_service

    # Act
    result = await usecase.execute(skip=0, limit=100)

    # Assert
    user_domain_service.validate_pagination_parameters.assert_called_once_with(0, 100)
    user_repository.find_all.assert_awaited_once()
    assert result == expected_users


async def test_get_users_success_with_pagination() -> None:
    """ページネーションが正しく動作することを確認する."""
    # Arrange
    all_users = [
        User(id=1, username="user1", email="user1@example.com"),
        User(id=2, username="user2", email="user2@example.com"),
        User(id=3, username="user3", email="user3@example.com"),
        User(id=4, username="user4", email="user4@example.com"),
        User(id=5, username="user5", email="user5@example.com"),
    ]

    user_repository = AsyncMock(spec=UserRepository)
    user_repository.find_all.return_value = all_users

    usecase = GetUsersUseCase(user_repository=user_repository)
    user_domain_service = Mock(spec=UserDomainService)
    usecase.user_domain_service = user_domain_service

    # Act
    result = await usecase.execute(skip=2, limit=2)

    # Assert
    user_domain_service.validate_pagination_parameters.assert_called_once_with(2, 2)
    user_repository.find_all.assert_awaited_once()
    assert result == [all_users[2], all_users[3]]


async def test_get_users_success_empty_list() -> None:
    """ユーザーが存在しない場合に空のリストが返されることを確認する."""
    # Arrange
    user_repository = AsyncMock(spec=UserRepository)
    user_repository.find_all.return_value = []

    usecase = GetUsersUseCase(user_repository=user_repository)
    user_domain_service = Mock(spec=UserDomainService)
    usecase.user_domain_service = user_domain_service

    # Act
    result = await usecase.execute(skip=0, limit=100)

    # Assert
    user_domain_service.validate_pagination_parameters.assert_called_once_with(0, 100)
    user_repository.find_all.assert_awaited_once()
    assert result == []


async def test_get_users_failure_limit_exceeds_maximum() -> None:
    """limit が 1000 を超える場合に ValidationException が発生することを確認する."""
    # Arrange
    user_repository = AsyncMock(spec=UserRepository)
    usecase = GetUsersUseCase(user_repository=user_repository)
    user_domain_service = Mock(spec=UserDomainService)
    user_domain_service.validate_pagination_parameters.side_effect = (
        ValidationException("Limit cannot exceed 1000", field_name="limit")
    )
    usecase.user_domain_service = user_domain_service

    # Act / Assert
    with pytest.raises(ValidationException, match="Limit cannot exceed 1000"):
        await usecase.execute(skip=0, limit=1001)

    user_domain_service.validate_pagination_parameters.assert_called_once_with(0, 1001)
    user_repository.find_all.assert_not_awaited()


async def test_get_users_failure_skip_negative() -> None:
    """skip が負の値の場合に ValidationException が発生することを確認する."""
    # Arrange
    user_repository = AsyncMock(spec=UserRepository)
    usecase = GetUsersUseCase(user_repository=user_repository)
    user_domain_service = Mock(spec=UserDomainService)
    user_domain_service.validate_pagination_parameters.side_effect = (
        ValidationException("Skip cannot be negative", field_name="skip")
    )
    usecase.user_domain_service = user_domain_service

    # Act / Assert
    with pytest.raises(ValidationException, match="Skip cannot be negative"):
        await usecase.execute(skip=-1, limit=100)

    user_domain_service.validate_pagination_parameters.assert_called_once_with(-1, 100)
    user_repository.find_all.assert_not_awaited()
