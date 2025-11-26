"""UpdateUserUseCaseのテスト."""

from unittest.mock import AsyncMock, Mock

import pytest

from app.domain.entities.user import User, UserRole
from app.domain.exceptions import UserNotFoundException, ValidationException
from app.domain.repositories.user_repository import UserRepository
from app.usecases.user.update_user_usecase import UpdateUserUseCase

pytestmark = pytest.mark.anyio("asyncio")


async def test_update_user_success(mock_transaction_manager: Mock) -> None:
    """ユーザー情報を更新できることを確認する."""
    # Arrange
    user_repository = AsyncMock(spec=UserRepository)
    existing_user = User(
        id=1,
        username="original_user",
        email="old@example.com",
        full_name="Old Name",
        role=UserRole.MEMBER,
    )
    user_repository.find_by_id.return_value = existing_user
    user_repository.update.return_value = existing_user

    usecase = UpdateUserUseCase(mock_transaction_manager, user_repository)
    usecase.user_domain_service = Mock()
    usecase.user_domain_service.validate_user_update_uniqueness = AsyncMock()

    new_username = "updated_user"
    new_email = "new@example.com"
    new_full_name = "New Name"

    # Act
    updated_user = await usecase.execute(
        user_id=existing_user.id or -1,
        username=new_username,
        email=new_email,
        full_name=new_full_name,
    )

    # Assert
    mock_transaction_manager.begin_transaction.assert_called_once()
    user_repository.find_by_id.assert_awaited_once_with(existing_user.id)
    usecase.user_domain_service.validate_user_update_uniqueness.assert_awaited_once_with(
        existing_user.id,
        existing_user,
        new_username,
        new_email,
        user_repository,
    )
    user_repository.update.assert_awaited_once_with(existing_user)

    assert updated_user is existing_user
    assert existing_user.username == new_username
    assert existing_user.email == new_email
    assert existing_user.full_name == new_full_name


async def test_update_user_failure_user_not_found(
    mock_transaction_manager: Mock,
) -> None:
    """存在しないユーザーを更新するとUserNotFoundExceptionとなる."""
    # Arrange
    user_repository = AsyncMock(spec=UserRepository)
    user_repository.find_by_id.return_value = None
    usecase = UpdateUserUseCase(mock_transaction_manager, user_repository)

    # Act / Assert
    with pytest.raises(UserNotFoundException):
        await usecase.execute(user_id=999, username="new")

    user_repository.find_by_id.assert_awaited_once_with(999)
    user_repository.update.assert_not_called()


async def test_update_user_failure_no_fields(
    mock_transaction_manager: Mock,
) -> None:
    """更新項目が無い場合はValidationExceptionとなる."""
    # Arrange
    user_repository = AsyncMock(spec=UserRepository)
    existing_user = User(
        id=1,
        username="original_user",
        email="old@example.com",
        full_name="Old Name",
        role=UserRole.MEMBER,
    )
    user_repository.find_by_id.return_value = existing_user
    usecase = UpdateUserUseCase(mock_transaction_manager, user_repository)
    usecase.user_domain_service = Mock()
    usecase.user_domain_service.validate_user_update_uniqueness = AsyncMock()

    # Act / Assert
    with pytest.raises(ValidationException, match="At least one field"):
        await usecase.execute(user_id=existing_user.id or -1)

    user_repository.find_by_id.assert_awaited_once_with(existing_user.id)
    usecase.user_domain_service.validate_user_update_uniqueness.assert_awaited_once_with(
        existing_user.id,
        existing_user,
        None,
        None,
        user_repository,
    )
    user_repository.update.assert_not_called()
