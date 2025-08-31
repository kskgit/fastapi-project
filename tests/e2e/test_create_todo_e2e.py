"""E2E tests for CreateTodoUseCase via HTTP endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCreateTodoE2E:
    """E2E tests for todo creation via HTTP API."""

    async def test_create_todo_minimal_data_success(
        self, test_client: AsyncClient, test_user
    ):
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
