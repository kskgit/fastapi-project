"""Integration tests for user creation with role assignment."""

from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.di.common import get_user_repository
from app.domain.entities import User
from app.domain.repositories import UserRepository
from main import app

USERS_ENDPOINT = "/api/v1/users/"


@pytest.mark.asyncio
class TestCreateUserIntegration:
    """Integration tests for creating users via HTTP API."""

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

    async def test_create_user_failure_unique_constraint(
        self,
        test_client: AsyncClient,
        test_user: User,
    ) -> None:
        """重複ユーザを作成しようとすると422になること."""
        # Arrange
        duplicate_payload = {
            "username": test_user.username,
            "email": test_user.email,
            "full_name": "Duplicated User",
            "role": "viewer",
        }

        # Act
        response = await test_client.post(USERS_ENDPOINT, json=duplicate_payload)

        # Assert
        assert response.status_code == 422
        response_data = response.json()
        assert "already exists" in response_data["detail"]

    async def test_create_user_failure_unexpected_exception(
        self,
        test_client: AsyncClient,
    ) -> None:
        """予期せぬ例外発生時は500となること."""
        # Arrange
        user_data = {
            "username": "unexpected_user",
            "email": "unexpected@example.com",
            "full_name": "Unexpected Failure",
            "role": "member",
        }
        failing_repository = AsyncMock(spec=UserRepository)
        failing_repository.find_by_username.return_value = None
        failing_repository.find_by_email.return_value = None
        failing_repository.create.side_effect = Exception("unexpected failure")
        app.dependency_overrides[get_user_repository] = lambda: failing_repository

        try:
            # Act
            response = await test_client.post(USERS_ENDPOINT, json=user_data)

            # Assert
            assert response.status_code == 500
            assert response.json()["detail"] == "Internal Server Error"
            failing_repository.create.assert_awaited_once()
        finally:
            app.dependency_overrides.pop(get_user_repository, None)
