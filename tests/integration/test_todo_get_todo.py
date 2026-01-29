"""Integration tests for GetTodoByIdUseCase via HTTP endpoints."""

from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.di.common import get_todo_repository
from app.domain.entities import User
from app.domain.repositories import TodoRepository
from main import app

TODOS_ENDPOINT = "/todos/"


@pytest.mark.asyncio
class TestGetTodoIntegration:
    """Integration tests for todo retrieval via HTTP API."""

    async def _create_todo(self, client: AsyncClient, user: User) -> int:
        """Helper to create a todo and return its ID."""
        response = await client.post(
            TODOS_ENDPOINT,
            json={
                "user_id": user.id,
                "title": "Parent todo for get test",
            },
        )
        assert response.status_code == 201
        return response.json()["id"]

    async def _create_subtask(
        self, client: AsyncClient, todo_id: int, user: User, title: str
    ) -> dict:
        """Helper to create a subtask and return response data."""
        response = await client.post(
            f"/todos/{todo_id}/subtasks",
            json={
                "user_id": user.id,
                "title": title,
            },
        )
        assert response.status_code == 201
        return response.json()

    async def test_get_todo_success_with_subtasks(
        self, test_client: AsyncClient, test_user: User
    ) -> None:
        """サブタスクを持つTodoを取得すると、subtasksフィールドにサブタスク一覧が含まれる。"""
        # Arrange
        todo_id = await self._create_todo(test_client, test_user)
        await self._create_subtask(test_client, todo_id, test_user, "Subtask 1")
        await self._create_subtask(test_client, todo_id, test_user, "Subtask 2")

        # Act
        response = await test_client.get(f"{TODOS_ENDPOINT}{todo_id}")

        # Assert - HTTP response
        assert response.status_code == 200
        response_data = response.json()

        # Assert - Todo fields
        assert response_data["id"] == todo_id
        assert response_data["title"] == "Parent todo for get test"

        # Assert - Subtasks included
        assert "subtasks" in response_data
        subtasks = response_data["subtasks"]
        assert len(subtasks) == 2

        subtask_titles = {s["title"] for s in subtasks}
        assert subtask_titles == {"Subtask 1", "Subtask 2"}

        # Assert - Subtask structure
        for subtask in subtasks:
            assert "id" in subtask
            assert "title" in subtask
            assert "is_completed" in subtask
            assert "created_at" in subtask
            assert "updated_at" in subtask

    async def test_get_todo_success_without_subtasks(
        self, test_client: AsyncClient, test_user: User
    ) -> None:
        """サブタスクを持たないTodoを取得すると、subtasksフィールドは空リストになる。"""
        # Arrange
        todo_id = await self._create_todo(test_client, test_user)

        # Act
        response = await test_client.get(f"{TODOS_ENDPOINT}{todo_id}")

        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == todo_id
        assert "subtasks" in response_data
        assert response_data["subtasks"] == []

    async def test_get_todo_failure_not_found(
        self, test_client: AsyncClient, test_user: User
    ) -> None:
        """存在しないtodo_idを指定すると404を返す。"""
        # Arrange
        non_existent_todo_id = 99999

        # Act
        response = await test_client.get(f"{TODOS_ENDPOINT}{non_existent_todo_id}")

        # Assert
        assert response.status_code == 404
        response_data = response.json()
        assert (
            response_data["detail"] == f"Todo with id {non_existent_todo_id} not found"
        )

    async def test_get_todo_failure_unexpected_exception(
        self, test_client: AsyncClient, test_user: User
    ) -> None:
        """予期せぬ例外が発生した場合は500を返す。"""
        # Arrange
        todo_id = await self._create_todo(test_client, test_user)

        # Repository をモックして予期せぬ例外を送出させる
        failing_repository = AsyncMock(spec=TodoRepository)
        failing_repository.find_by_id.side_effect = Exception("unexpected_exception")

        # Override the repository dependency only
        app.dependency_overrides[get_todo_repository] = lambda: failing_repository

        try:
            # Act
            response = await test_client.get(f"{TODOS_ENDPOINT}{todo_id}")

            # Assert - Should return 500 Internal Server Error
            assert response.status_code == 500
            response_data = response.json()
            assert "Internal Server Error" in response_data["detail"]
            failing_repository.find_by_id.assert_awaited_once()
        finally:
            # Clean up - Remove the override
            app.dependency_overrides.pop(get_todo_repository, None)
