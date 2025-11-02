"""E2E tests for CreateTodoUseCase via HTTP endpoints."""

from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from sqlalchemy import text

from app.composition.di import get_todo_repository
from app.domain.entities.user import User
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.sqlalchemy_todo_repository import (
    SQLAlchemyTodoRepository,
)
from main import app

TODOS_ENDPOINT = "/todos/"


@pytest.mark.asyncio
class TestCreateTodoE2E:
    """E2E tests for todo creation via HTTP API."""

    async def test_create_todo_success_minimal_data(
        self, test_client: AsyncClient, test_user: User
    ) -> None:
        """Test successful todo creation with minimal data via HTTP."""
        # Arrange
        todo_data = {
            "user_id": test_user.id,
            "title": "Complete project documentation",
        }

        # Act
        response = await test_client.post(TODOS_ENDPOINT, json=todo_data)

        # Assert - HTTP response
        assert response.status_code == 201
        response_data = response.json()

        # Assert - Response structure
        assert "id" in response_data
        assert response_data["title"] == todo_data["title"]
        assert response_data["description"] is None
        assert response_data["due_date"] is None
        assert response_data["priority"] == "medium"
        assert response_data["status"] == "pending"
        assert "created_at" in response_data
        assert "updated_at" in response_data

        # Assert - Verify todo was actually created in database via GET
        todo_id = response_data["id"]
        get_response = await test_client.get(f"{TODOS_ENDPOINT}{todo_id}")
        assert get_response.status_code == 200

        get_data = get_response.json()
        assert get_data["title"] == todo_data["title"]
        assert get_data["id"] == todo_id

    async def test_create_todo_failure_missing_user_id(
        self, test_client: AsyncClient, test_user: User
    ) -> None:
        """user_id未指定の場合は422 Unprocessable Entityを返す."""
        # Arrange
        todo_data = {
            "title": "Complete project documentation",
        }

        # Act
        response = await test_client.post(TODOS_ENDPOINT, json=todo_data)

        # Assert
        assert response.status_code == 422
        response_data = response.json()
        assert response_data["detail"][0]["msg"] == "Field required"
        assert response_data["detail"][0]["loc"] == ["body", "user_id"]

    async def test_create_todo_failure_title_too_short(
        self, test_client: AsyncClient, test_user: User
    ) -> None:
        """Validationエラー: タイトルがトリム後に3文字未満の場合は400を返す."""
        # Arrange
        todo_data = {
            "user_id": test_user.id,
            "title": "  ab ",
        }

        # Act
        response = await test_client.post(TODOS_ENDPOINT, json=todo_data)

        # Assert
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["detail"] == (
            "Title must be at least 3 characters long after removing whitespace"
        )

    async def test_create_todo_failure_user_not_found(
        self, test_client: AsyncClient, test_user: User
    ) -> None:
        """Test todo creation fails when user does not exist."""
        # Arrange
        todo_data = {
            "user_id": 9999,
            "title": "Complete project documentation",
            "description": "Write comprehensive documentation",
        }

        # Act
        response = await test_client.post(TODOS_ENDPOINT, json=todo_data)

        # Assert - Should return 404 User Not Found
        assert response.status_code == 404
        response_data = response.json()
        assert response_data["detail"] == "User with id 9999 not found"

    async def test_create_todo_failure_data_operation_exception(
        self, test_client: AsyncClient, test_user: User
    ) -> None:
        """DB操作エラーを発生させて500応答となることを確認する。"""
        # Arrange
        todo_data = {
            "user_id": test_user.id,
            "title": "Complete project documentation",
            "description": "Write comprehensive documentation",
        }

        # Drop the todos table to force SQLAlchemy to raise an error during INSERT.
        get_db_override = app.dependency_overrides.get(get_db)
        if get_db_override is None:
            pytest.fail("Database dependency override is not configured for tests.")

        test_db_session = await get_db_override()
        if test_db_session.get_bind() is None:
            pytest.fail("AsyncSession must be bound to an engine.")

        await test_db_session.execute(text("DROP TABLE todos"))
        await test_db_session.commit()

        # Act
        response = await test_client.post(TODOS_ENDPOINT, json=todo_data)

        # Assert - Should return 500 Internal Server Error
        assert response.status_code == 500
        response_data = response.json()
        assert "Failed to execute data operation" in response_data["detail"]

    async def test_create_todo_failure_unexpected_exception(
        self, test_client: AsyncClient, test_user: User
    ) -> None:
        """Test todo creation fails when database persistence error occurs."""
        # Arrange
        todo_data = {
            "user_id": test_user.id,
            "title": "Complete project documentation",
            "description": "Write comprehensive documentation",
        }
        # Repository をモックして予期せぬ例外を送出させる
        todo_repository_mock = AsyncMock(spec=SQLAlchemyTodoRepository)
        todo_repository_mock.create.side_effect = Exception("unexpected_exception")

        # Override the repository dependency only
        app.dependency_overrides[get_todo_repository] = lambda: todo_repository_mock

        try:
            # Act
            response = await test_client.post(TODOS_ENDPOINT, json=todo_data)

            # Assert - Should return 500 Internal Server Error
            assert response.status_code == 500
            response_data = response.json()
            assert "Internal Server Error" in response_data["detail"]
            todo_repository_mock.create.assert_awaited_once()
        finally:
            # Clean up - Remove the override
            if get_todo_repository in app.dependency_overrides:
                del app.dependency_overrides[get_todo_repository]
