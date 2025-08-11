"""CreateUserUseCase失敗時の動作確認テスト"""

from unittest.mock import Mock

import pytest

from app.domain.entities.user import User
from app.domain.exceptions import ConnectionException
from app.domain.exceptions.business import UniqueConstraintException
from app.domain.repositories.user_repository import UserRepository
from app.usecases.user.create_user_usecase import CreateUserUseCase


def test_create_user_failure_username_already_exists():
    """ユーザー名重複時のValueError発生を確認"""

    # モックRepositoryを作成
    mock_user_repository = Mock(spec=UserRepository)

    # 既存ユーザーが存在する設定（ユーザー名重複）
    existing_user = User(id=1, username="existing_user", email="existing@example.com")
    mock_user_repository.find_by_username.return_value = existing_user
    mock_user_repository.find_by_email.return_value = None  # メールは重複なし

    # UseCaseを初期化
    usecase = CreateUserUseCase(mock_user_repository)

    # テスト実行: ValueErrorが発生することを確認
    with pytest.raises(
        UniqueConstraintException, match="Username 'existing_user' already exists"
    ):
        usecase.execute(
            username="existing_user", email="new@example.com", full_name="New User"
        )

    # Repository呼び出し確認
    mock_user_repository.find_by_username.assert_called_once_with("existing_user")
    # ユーザー名重複で処理が停止するため、find_by_emailは呼ばれない
    mock_user_repository.find_by_email.assert_not_called()
    # saveは呼ばれないことを確認
    mock_user_repository.save.assert_not_called()

    print("✅ テスト成功: ユーザー名重複時にValueErrorが発生")


def test_create_user_failure_connection_error():
    """データ永続化接続失敗時のConnectionException発生を確認"""
    # Arrange
    mock_user_repository = Mock(spec=UserRepository)
    mock_user_repository.find_by_username.return_value = None
    mock_user_repository.find_by_email.return_value = None
    mock_user_repository.save.side_effect = ConnectionException(
        "Failed to establish connection to data persistence layer"
    )

    usecase = CreateUserUseCase(mock_user_repository)

    # Act/Assert
    with pytest.raises(
        ConnectionException,
        match="Failed to establish connection to data persistence layer",
    ):
        usecase.execute(
            username="new_user", email="new@example.com", full_name="New User"
        )

    mock_user_repository.find_by_username.assert_called_once_with("new_user")
    mock_user_repository.find_by_email.assert_called_once_with("new@example.com")
    mock_user_repository.save.assert_called_once()


if __name__ == "__main__":
    test_create_user_failure_username_already_exists()
    test_create_user_failure_connection_error()
    print("\n🎯 CreateUserUseCase失敗テスト完了")
    print("💡 Exception Handlerがこれらの例外を適切なHTTPエラーに変換します")
    print("   - ValueError → HTTP 400 (Bad Request)")
    print("   - ConnectionException → HTTP 503 (Service Unavailable)")
