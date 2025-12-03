"""CreateUserUseCase失敗時の動作確認テスト"""

from unittest.mock import AsyncMock, Mock

import pytest

from app.domain.entities.user import User, UserRole
from app.domain.exceptions import ConnectionException
from app.domain.exceptions.business import UniqueConstraintException
from app.domain.repositories.user_repository import UserRepository
from app.usecases.user.create_user_usecase import CreateUserUseCase

pytestmark = pytest.mark.anyio("asyncio")


def _set_up(
    mock_transaction_manager: Mock,
) -> tuple[CreateUserUseCase, AsyncMock, AsyncMock]:
    user_repository = AsyncMock(spec=UserRepository)
    usecase = CreateUserUseCase(mock_transaction_manager, user_repository)
    user_domain_service = AsyncMock()
    usecase.user_domain_service = user_domain_service
    return usecase, user_repository, user_domain_service


async def test_create_user_success_assigns_role(
    mock_transaction_manager: Mock,
) -> None:
    """指定したroleが永続化対象Userに設定されることを確認する."""
    # Arrange
    usecase, mock_user_repository, user_domain_service = _set_up(
        mock_transaction_manager
    )
    saved_user = User(
        id=10,
        username="viewer_user",
        email="viewer@example.com",
        full_name="Viewer User",
        role=UserRole.VIEWER,
    )
    mock_user_repository.create.return_value = saved_user

    # Act
    result = await usecase.execute(
        username="viewer_user",
        email="viewer@example.com",
        full_name="Viewer User",
        role=UserRole.VIEWER,
    )

    # Assert
    mock_transaction_manager.begin_transaction.assert_called_once()
    user_domain_service.validate_user_uniqueness.assert_awaited_once_with(
        username="viewer_user",
        email="viewer@example.com",
        user_repository=mock_user_repository,
    )
    mock_user_repository.create.assert_awaited_once()
    save_call = mock_user_repository.create.call_args
    assert save_call is not None
    saved_entity = save_call.args[0]
    assert isinstance(saved_entity, User)
    assert saved_entity.role == UserRole.VIEWER
    assert result == saved_user


async def test_create_user_failure_username_already_exists(
    mock_transaction_manager: Mock,
):
    """ユーザー名重複時のValueError発生を確認"""
    # Arrange
    mock_user_repository = Mock(spec=UserRepository)
    existing_user = User(id=1, username="existing_user", email="existing@example.com")
    mock_user_repository.find_by_username.return_value = existing_user
    mock_user_repository.find_by_email.return_value = None  # メールは重複なし

    usecase = CreateUserUseCase(mock_transaction_manager, mock_user_repository)

    # Act/Assert
    with pytest.raises(
        UniqueConstraintException, match="Username 'existing_user' already exists"
    ):
        await usecase.execute(
            username="existing_user",
            email="new@example.com",
            full_name="New User",
            role=UserRole.MEMBER,
        )

    mock_user_repository.find_by_username.assert_called_once_with("existing_user")
    mock_user_repository.find_by_email.assert_not_called()
    mock_user_repository.create.assert_not_called()


async def test_create_user_failure_connection_error(
    mock_transaction_manager: Mock,
):
    """データ永続化接続失敗時のConnectionException発生を確認"""
    # Arrange
    mock_user_repository = Mock(spec=UserRepository)
    mock_user_repository.find_by_username.return_value = None
    mock_user_repository.find_by_email.return_value = None
    mock_user_repository.create.side_effect = ConnectionException(
        "Failed to establish connection to data persistence layer"
    )

    usecase = CreateUserUseCase(mock_transaction_manager, mock_user_repository)

    # Act/Assert
    with pytest.raises(
        ConnectionException,
        match="Failed to establish connection to data persistence layer",
    ):
        await usecase.execute(
            username="new_user",
            email="new@example.com",
            full_name="New User",
            role=UserRole.MEMBER,
        )

    mock_user_repository.find_by_username.assert_called_once_with("new_user")
    mock_user_repository.find_by_email.assert_called_once_with("new@example.com")
    mock_user_repository.create.assert_called_once()
