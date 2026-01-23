"""Integration tests for Subtask creation endpoints."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.di.common import get_todo_repository
from app.domain.entities.user import User, UserRole
from app.domain.repositories.todo_repository import TodoRepository
from app.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from main import app

TODOS_ENDPOINT = "/todos/"
SUBTASKS_ENDPOINT_TEMPLATE = "/todos/{todo_id}/subtasks"


@pytest.mark.asyncio
class TestCreateSubtaskIntegration:
    """Integration tests for subtask creation via HTTP API."""

    async def _create_todo(self, client: AsyncClient, user: User) -> int:
        """Helper to create a todo and return its ID."""
        response = await client.post(
            TODOS_ENDPOINT,
            json={
                "user_id": user.id,
                "title": "Parent todo for subtask",
            },
        )
        assert response.status_code == 201
        return response.json()["id"]

    async def test_create_subtask_success(
        self, test_client: AsyncClient, test_user: User
    ) -> None:
        """サブタスクの作成に成功すると201と作成結果を返す。"""
        # Arrange
        todo_id = await self._create_todo(test_client, test_user)
        subtask_data = {
            "user_id": test_user.id,
            "title": "Write unit tests",
        }

        # Act
        response = await test_client.post(
            SUBTASKS_ENDPOINT_TEMPLATE.format(todo_id=todo_id), json=subtask_data
        )

        # Assert
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["title"] == subtask_data["title"]
        assert response_data["todo_id"] == todo_id
        assert response_data["is_completed"] is False
        assert response_data["completed_at"] is None
        assert "id" in response_data
        assert "created_at" in response_data
        assert "updated_at" in response_data

    async def test_create_subtask_failure_missing_title(
        self, test_client: AsyncClient, test_user: User
    ) -> None:
        """titleが必須のため未指定だと422を返す。"""
        # Arrange
        todo_id = await self._create_todo(test_client, test_user)
        subtask_data = {
            "user_id": test_user.id,
        }

        # Act
        response = await test_client.post(
            SUBTASKS_ENDPOINT_TEMPLATE.format(todo_id=todo_id), json=subtask_data
        )

        # Assert
        assert response.status_code == 422
        response_data = response.json()
        assert response_data["detail"][0]["msg"] == "Field required"
        assert response_data["detail"][0]["loc"] == ["body", "title"]

    async def test_create_subtask_failure_user_not_found(
        self, test_client: AsyncClient, test_user: User
    ) -> None:
        """存在しないユーザーIDを指定すると404を返す。"""
        # Arrange
        todo_id = await self._create_todo(test_client, test_user)
        non_existent_user_id = 99999
        subtask_data = {
            "user_id": non_existent_user_id,
            "title": "Write unit tests",
        }

        # Act
        response = await test_client.post(
            SUBTASKS_ENDPOINT_TEMPLATE.format(todo_id=todo_id), json=subtask_data
        )

        # Assert
        assert response.status_code == 404
        response_data = response.json()
        assert (
            response_data["detail"] == f"User with id {non_existent_user_id} not found"
        )

    async def test_create_subtask_failure_todo_not_found(
        self, test_client: AsyncClient, test_user: User
    ) -> None:
        """存在しないtodo_idを指定すると404を返す。"""
        # Arrange
        non_existent_todo_id = 99999
        subtask_data = {
            "user_id": test_user.id,
            "title": "Write unit tests",
        }

        # Act
        response = await test_client.post(
            SUBTASKS_ENDPOINT_TEMPLATE.format(todo_id=non_existent_todo_id),
            json=subtask_data,
        )

        # Assert
        assert response.status_code == 404
        response_data = response.json()
        assert (
            response_data["detail"] == f"Todo with id {non_existent_todo_id} not found"
        )

    async def test_create_subtask_failure_todo_user_mismatch(
        self, test_client: AsyncClient, test_user: User, test_db_session
    ) -> None:
        """他のユーザーのTodoに対してサブタスクを作成しようとすると404を返す。"""
        # Arrange - Create another user
        user_repo = SQLAlchemyUserRepository(test_db_session)
        another_user = User.create(
            username="another_user",
            email="another@example.com",
            full_name="Another User",
        )
        saved_another_user = await user_repo.create(another_user)
        await test_db_session.commit()

        # Create a todo owned by another_user
        todo_response = await test_client.post(
            TODOS_ENDPOINT,
            json={
                "user_id": saved_another_user.id,
                "title": "Another user's todo",
            },
        )
        assert todo_response.status_code == 201
        todo_id = todo_response.json()["id"]

        # Try to create a subtask for another user's todo
        subtask_data = {
            "user_id": test_user.id,
            "title": "Write unit tests",
        }

        # Act
        response = await test_client.post(
            SUBTASKS_ENDPOINT_TEMPLATE.format(todo_id=todo_id), json=subtask_data
        )

        # Assert
        assert response.status_code == 404
        response_data = response.json()
        assert response_data["detail"] == f"Todo with id {todo_id} not found"

    async def test_create_subtask_failure_user_permission_denied(
        self, test_client: AsyncClient, test_user: User, test_db_session
    ) -> None:
        """VIEWER権限のユーザーがサブタスクを作成しようとすると403を返す。"""
        # Arrange - Create a VIEWER user
        user_repo = SQLAlchemyUserRepository(test_db_session)
        viewer_user = User.create(
            username="viewer_user",
            email="viewer@example.com",
            full_name="Viewer User",
            role=UserRole.VIEWER,
        )
        saved_viewer_user = await user_repo.create(viewer_user)
        await test_db_session.commit()

        # Create a todo owned by the viewer user
        todo_response = await test_client.post(
            TODOS_ENDPOINT,
            json={
                "user_id": saved_viewer_user.id,
                "title": "Viewer's todo",
            },
        )
        assert todo_response.status_code == 201
        todo_id = todo_response.json()["id"]

        # Try to create a subtask as the viewer user
        subtask_data = {
            "user_id": saved_viewer_user.id,
            "title": "Write unit tests",
        }

        # Act
        response = await test_client.post(
            SUBTASKS_ENDPOINT_TEMPLATE.format(todo_id=todo_id), json=subtask_data
        )

        # Assert
        assert response.status_code == 403
        response_data = response.json()
        assert (
            response_data["detail"]
            == f"User with id {saved_viewer_user.id} lacks required permissions"
        )

    async def test_create_subtask_failure_unexpected_exception(
        self, test_client: AsyncClient, test_user: User
    ) -> None:
        """予期せぬ例外が発生した場合は500を返す。"""
        # Arrange
        todo_id = await self._create_todo(test_client, test_user)
        subtask_data = {
            "user_id": test_user.id,
            "title": "Write unit tests",
        }

        # Repository をモックして予期せぬ例外を送出させる
        failing_repository = AsyncMock(spec=TodoRepository)
        failing_repository.find_by_id.side_effect = Exception("unexpected_exception")

        # Override the repository dependency only
        app.dependency_overrides[get_todo_repository] = lambda: failing_repository

        try:
            # Act
            response = await test_client.post(
                SUBTASKS_ENDPOINT_TEMPLATE.format(todo_id=todo_id), json=subtask_data
            )

            # Assert - Should return 500 Internal Server Error
            assert response.status_code == 500
            response_data = response.json()
            assert "Internal Server Error" in response_data["detail"]
            failing_repository.find_by_id.assert_awaited_once()
        finally:
            # Clean up - Remove the override
            app.dependency_overrides.pop(get_todo_repository, None)
