"""E2E tests for Subtask creation endpoints."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.di.common import get_todo_repository
from app.domain.entities.user import User
from app.domain.repositories.todo_repository import TodoRepository
from main import app

TODOS_ENDPOINT = "/todos/"
SUBTASKS_ENDPOINT_TEMPLATE = "/todos/{todo_id}/subtasks"


@pytest.mark.asyncio
class TestCreateSubtaskE2E:
    """E2E tests for subtask creation via HTTP API."""

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
        """ユーザが存在しないと400を返す。"""
        # Arrange
        todo_id = await self._create_todo(test_client, test_user)
        subtask_data = {
            "user_id": 9999,
            "title": "Write unit tests",
        }

        # Act
        response = await test_client.post(
            SUBTASKS_ENDPOINT_TEMPLATE.format(todo_id=todo_id), json=subtask_data
        )

        # Assert
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["detail"] == "User with id 9999 not found"

    async def test_create_subtask_failure_todo_not_found(
        self, test_client: AsyncClient, test_user: User
    ) -> None:
        """Todoが存在しないと400を返す。"""
        # Arrange
        todo_id = 9999
        subtask_data = {
            "user_id": test_user.id,
            "title": "Write unit tests",
        }

        # Act
        response = await test_client.post(
            SUBTASKS_ENDPOINT_TEMPLATE.format(todo_id=todo_id), json=subtask_data
        )

        # Assert
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["detail"] == "Todo with id 9999 not found"

    async def test_create_subtask_failure_unexpected_exception(
        self, test_client: AsyncClient, test_user: User
    ) -> None:
        """Repositoryで予期せぬ例外が発生すると500を返す。"""
        # Arrange
        todo_id = await self._create_todo(test_client, test_user)
        subtask_data = {
            "user_id": test_user.id,
            "title": "Handle failure case",
        }
        failing_repository = AsyncMock(spec=TodoRepository)
        failing_repository.find_by_id.side_effect = Exception("unexpected_exception")
        app.dependency_overrides[get_todo_repository] = lambda: failing_repository

        try:
            # Act
            response = await test_client.post(
                SUBTASKS_ENDPOINT_TEMPLATE.format(todo_id=todo_id), json=subtask_data
            )

            # Assert
            assert response.status_code == 500
            response_data = response.json()
            assert "Internal Server Error" in response_data["detail"]
            failing_repository.find_by_id.assert_awaited_once()
        finally:
            app.dependency_overrides.pop(get_todo_repository, None)
