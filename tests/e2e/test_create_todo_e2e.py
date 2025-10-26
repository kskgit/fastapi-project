"""E2E tests for CreateTodoUseCase via HTTP endpoints."""

from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.composition.di import get_create_todo_usecase
from app.domain.exceptions.business import UserNotFoundException
from app.domain.exceptions.system import DataOperationException
from main import app


@pytest.mark.asyncio
class TestCreateTodoE2E:
    """E2E tests for todo creation via HTTP API."""

    async def test_create_todo_minimal_data_success(
        self, test_client: AsyncClient, test_user: object
    ) -> None:
        """Test successful todo creation with minimal data via HTTP."""
        # Arrange
        todo_data = {
            "title": "Complete project documentation",
        }

        # Act
        response = await test_client.post("/todos/", json=todo_data)

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
        get_response = await test_client.get(f"/todos/{todo_id}")
        assert get_response.status_code == 200

        get_data = get_response.json()
        assert get_data["title"] == todo_data["title"]
        assert get_data["id"] == todo_id

    async def test_create_todo_validation_error_title_too_short(
        self, test_client: AsyncClient, test_user: object
    ) -> None:
        """Validationエラー: タイトルがトリム後に3文字未満の場合は400を返す."""
        # Arrange
        todo_data = {
            "title": "  ab ",
        }

        # Act
        response = await test_client.post("/todos/", json=todo_data)

        # Assert
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["detail"] == (
            "Title must be at least 3 characters long after removing whitespace"
        )

    async def test_create_todo_user_not_found(self, test_client: AsyncClient) -> None:
        """Test todo creation fails when user does not exist."""
        # Arrange
        todo_data = {
            "title": "Complete project documentation",
            "description": "Write comprehensive documentation",
        }

        # Mock the CreateTodoUseCase to raise UserNotFoundException
        mock_usecase = AsyncMock()
        mock_usecase.execute.side_effect = UserNotFoundException(999)

        # Override the dependency
        app.dependency_overrides[get_create_todo_usecase] = lambda: mock_usecase

        try:
            # Act
            response = await test_client.post("/todos/", json=todo_data)

            # Assert - Should return 404 User Not Found
            assert response.status_code == 404
            response_data = response.json()
            assert "detail" in response_data
            assert "User with id 999 not found" in response_data["detail"]
        finally:
            # Clean up - Remove the override
            if get_create_todo_usecase in app.dependency_overrides:
                del app.dependency_overrides[get_create_todo_usecase]

    async def test_create_todo_data_persistence_exception(
        self, test_client: AsyncClient
    ) -> None:
        """Test todo creation fails when database persistence error occurs."""
        # Arrange
        todo_data = {
            "title": "Complete project documentation",
            "description": "Write comprehensive documentation",
        }

        # Mock the CreateTodoUseCase to raise DataPersistenceException
        mock_usecase = AsyncMock()
        mock_usecase.execute.side_effect = DataOperationException(
            operation_name="TestClass.test_method",
        )

        # Override the dependency
        app.dependency_overrides[get_create_todo_usecase] = lambda: mock_usecase

        try:
            # Act
            response = await test_client.post("/todos/", json=todo_data)

            # Assert - Should return 500 Internal Server Error
            assert response.status_code == 500
            response_data = response.json()
            assert "Failed to execute data operation" in response_data["detail"]
        finally:
            # Clean up - Remove the override
            if get_create_todo_usecase in app.dependency_overrides:
                del app.dependency_overrides[get_create_todo_usecase]
