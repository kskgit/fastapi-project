"""ユーザ削除エンドポイントのインテグレーションテスト."""

from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.di.common import get_todo_repository
from app.domain.entities.todo import Todo
from app.domain.entities.user import User
from app.domain.repositories.todo_repository import TodoRepository
from main import app

USERS_ENDPOINT = "/api/v1/users/"


@pytest.mark.asyncio
class TestDeleteUserIntegration:
    """ユーザ削除処理のインテグレーションテストを集約."""

    async def test_delete_user_success_removes_related_todos(
        self,
        test_client: AsyncClient,
        test_db_session,
        test_user: User,
    ) -> None:
        """ユーザ削除時に関連TODOも削除されること."""
        # Arrange
        assert test_user.id is not None
        user_id = test_user.id
        todo_repository = get_todo_repository(test_db_session)
        todo = Todo.create(
            title="Cleanup todo",
            user_id=user_id,
            description="Should disappear with the user",
        )
        await todo_repository.create(todo)
        await test_db_session.commit()

        # Act
        response = await test_client.delete(f"{USERS_ENDPOINT}{user_id}")

        # Assert - HTTP response
        assert response.status_code == 204

        # Assert - User no longer retrievable
        get_response = await test_client.get(f"{USERS_ENDPOINT}{user_id}")
        assert get_response.status_code == 404
        assert get_response.json()["detail"] == f"User with id {user_id} not found"

        # Assert - Related todos are removed
        remaining_todos = await todo_repository.find_with_pagination(user_id=user_id)
        assert remaining_todos == []

    async def test_delete_user_failure_when_not_found(
        self,
        test_client: AsyncClient,
    ) -> None:
        """存在しないユーザを削除しようとすると404となること."""
        # Arrange
        missing_user_id = 9999

        # Act
        response = await test_client.delete(f"{USERS_ENDPOINT}{missing_user_id}")

        # Assert
        assert response.status_code == 404
        response_data = response.json()
        assert response_data["detail"] == f"User with id {missing_user_id} not found"

    async def test_delete_user_failure_unexpected_exception(
        self,
        test_client: AsyncClient,
        test_user: User,
    ) -> None:
        """予期せぬ例外発生時に500を返すこと."""
        # Arrange
        assert test_user.id is not None
        user_id = test_user.id
        failing_todo_repository = AsyncMock(spec=TodoRepository)
        failing_todo_repository.delete_all_by_user_id.side_effect = Exception(
            "unexpected failure"
        )
        app.dependency_overrides[get_todo_repository] = lambda: failing_todo_repository

        try:
            # Act
            response = await test_client.delete(f"{USERS_ENDPOINT}{user_id}")

            # Assert
            assert response.status_code == 500
            response_data = response.json()
            assert response_data["detail"] == "Internal Server Error"
            failing_todo_repository.delete_all_by_user_id.assert_awaited_once_with(
                user_id
            )
        finally:
            app.dependency_overrides.pop(get_todo_repository, None)
