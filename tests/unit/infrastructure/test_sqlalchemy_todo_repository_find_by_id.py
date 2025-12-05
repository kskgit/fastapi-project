"""Tests for SQLAlchemyTodoRepository.find_by_id."""

import pytest

from app.infrastructure.repositories.sqlalchemy_todo_repository import (
    SQLAlchemyTodoRepository,
)


@pytest.mark.asyncio
class TestSQLAlchemyTodoRepositoryFindById:
    """Unit tests covering the find_by_id method behaviour."""

    async def test_find_by_id_failure_not_found(self, repo_db_session):
        """存在しないTodoの場合にNoneが返ることを確認する。"""
        # Arrange
        repository = SQLAlchemyTodoRepository(repo_db_session)

        # Act
        result = await repository.find_by_id(999)

        # Assert
        assert result is None
