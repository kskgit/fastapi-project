"""Tests for UserDomainService."""

from unittest.mock import AsyncMock

import pytest

from app.domain.entities.user import User, UserRole
from app.domain.exceptions import UniqueConstraintException
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.user_domain_service import UserDomainService

pytestmark = [pytest.mark.anyio("asyncio")]


async def test_validate_user_uniqueness_failure_duplicate_username() -> None:
    """ユーザー作成時に重複ユーザー名を検知できること."""
    # Arrange
    user_repository = AsyncMock(spec=UserRepository)
    user_repository.find_by_username.return_value = User(
        id=2,
        username="duplicate_user",
        email="taken@example.com",
        role=UserRole.MEMBER,
    )
    user_repository.find_by_email.return_value = None
    service = UserDomainService()

    # Act
    async def act() -> None:
        await service.validate_user_uniqueness(
            username="duplicate_user",
            email="new_user@example.com",
            user_repository=user_repository,
        )

    # Assert
    with pytest.raises(UniqueConstraintException, match="duplicate_user"):
        await act()


async def test_validate_user_uniqueness_failure_other_user_email() -> None:
    """ユーザー更新時に別ユーザーのメール重複を検知できること."""
    # Arrange
    user_repository = AsyncMock(spec=UserRepository)
    conflicting_user = User(
        id=3,
        username="other_user",
        email="shared@example.com",
        role=UserRole.MEMBER,
    )
    user_repository.find_by_username.return_value = None
    user_repository.find_by_email.return_value = conflicting_user
    service = UserDomainService()

    # Act
    async def act() -> None:
        await service.validate_user_uniqueness(
            username="current_user",
            email="shared@example.com",
            user_repository=user_repository,
        )

    # Assert
    with pytest.raises(UniqueConstraintException, match="Email"):
        await act()
