"""E2E tests for user creation with role assignment."""

import pytest
from httpx import AsyncClient

USERS_ENDPOINT = "/api/v1/users/"


@pytest.mark.asyncio
class TestCreateUserE2E:
    """Tests for creating users via HTTP API."""

    async def test_create_user_success_viewer_role(
        self, test_client: AsyncClient
    ) -> None:
        """閲覧専用ロール(viewer)でユーザを作成できることを確認する。"""
        # Arrange
        user_data = {
            "username": "viewer_user",
            "email": "viewer@example.com",
            "full_name": "Viewer User",
            "role": "viewer",
        }

        # Act
        response = await test_client.post(USERS_ENDPOINT, json=user_data)

        # Assert - HTTP response
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["username"] == user_data["username"]
        assert response_data["email"] == user_data["email"]
        assert response_data["full_name"] == user_data["full_name"]
        assert response_data["role"] == "viewer"
        assert response_data["is_active"] is True

        # Assert - persisted state
        created_user_id = response_data["id"]
        get_response = await test_client.get(f"{USERS_ENDPOINT}{created_user_id}")
        assert get_response.status_code == 200
        persisted = get_response.json()
        assert persisted["id"] == created_user_id
        assert persisted["role"] == "viewer"
