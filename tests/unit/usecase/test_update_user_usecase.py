"""UpdateUserUseCaseのテスト."""

from unittest.mock import AsyncMock, Mock

import pytest

from app.domain.entities.user import User, UserRole
from app.domain.exceptions import UserNotFoundException, ValidationException
from app.domain.repositories.user_repository import UserRepository
from app.usecases.user.update_user_usecase import UpdateUserUseCase

pytestmark = pytest.mark.anyio("asyncio")


def _set_up(
    existing_user: User, mock_transaction_manager: Mock
) -> tuple[UpdateUserUseCase, AsyncMock, AsyncMock]:
    user_repository = AsyncMock(spec=UserRepository)
    user_repository.find_by_id.return_value = existing_user
    # 引数で受け取ったuserをそのまま返却する
    user_repository.update.side_effect = lambda user: user

    usecase = UpdateUserUseCase(mock_transaction_manager, user_repository)
    user_domain_service = AsyncMock()
    usecase.user_domain_service = user_domain_service

    return usecase, user_repository, user_domain_service


async def test_update_user_success(mock_transaction_manager: Mock) -> None:
    """ユーザー情報を更新できることを確認する."""
    # Arrange
    existing_user = User(
        id=1,
        username="old_user",
        email="old@example.com",
        full_name="Old Name",
        role=UserRole.MEMBER,
    )

    usecase, user_repository, domain_service = _set_up(
        existing_user=existing_user, mock_transaction_manager=mock_transaction_manager
    )

    new_username = "new_user"
    new_email = "new@example.com"
    new_full_name = "New Name"
    new_role = UserRole.VIEWER

    # Act
    updated_user = await usecase.execute(
        user_id=existing_user.id or -1,
        username=new_username,
        email=new_email,
        full_name=new_full_name,
        role=new_role,
    )

    # Assert
    mock_transaction_manager.begin_transaction.assert_called_once()
    user_repository.find_by_id.assert_awaited_once_with(existing_user.id)
    domain_service.validate_user_uniqueness.assert_awaited_once_with(
        username=new_username,
        email=new_email,
        user_repository=user_repository,
    )

    assert existing_user.username == new_username
    assert existing_user.email == new_email
    assert existing_user.full_name == new_full_name
    assert existing_user.role == new_role
    user_repository.update.assert_awaited_once_with(existing_user)

    assert updated_user.username == new_username
    assert updated_user.email == new_email
    assert updated_user.full_name == new_full_name
    assert updated_user.role == new_role


async def test_update_user_success_not_call_unique_check(
    mock_transaction_manager: Mock,
) -> None:
    """ユーザー情報を更新できることを確認する.

    ユーザ名、emailが更新されない場合、重複チェックが行われないこと
    """
    # Arrange
    existing_user = User(
        id=1,
        username="old_user",
        email="old@example.com",
        full_name="Old Name",
        role=UserRole.MEMBER,
    )

    usecase, user_repository, domain_service = _set_up(
        existing_user=existing_user, mock_transaction_manager=mock_transaction_manager
    )

    new_username = "old_user"
    new_email = "old@example.com"
    new_full_name = "Old Name"
    new_role = UserRole.VIEWER

    # Act
    updated_user = await usecase.execute(
        user_id=existing_user.id or -1,
        username=new_username,
        email=new_email,
        full_name=new_full_name,
        role=new_role,
    )

    # Assert
    mock_transaction_manager.begin_transaction.assert_called_once()
    user_repository.find_by_id.assert_awaited_once_with(existing_user.id)
    domain_service.validate_user_uniqueness.assert_not_called()
    user_repository.update.assert_awaited_once_with(existing_user)

    assert updated_user.username == existing_user.username
    assert updated_user.email == existing_user.email
    assert updated_user.role == new_role


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
    usecase.user_domain_service.validate_user_uniqueness = AsyncMock()

    # Act / Assert
    with pytest.raises(ValidationException, match="At least one field"):
        await usecase.execute(user_id=existing_user.id or -1)

    user_repository.find_by_id.assert_awaited_once_with(existing_user.id)
    usecase.user_domain_service.validate_user_uniqueness.assert_not_called()
    user_repository.update.assert_not_called()
