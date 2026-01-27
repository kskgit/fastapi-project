"""Tests for SQLAlchemySubTaskRepository.create."""

import pytest
from sqlalchemy import select

from app.domain import SubTask
from app.infrastructure.database.models.subtask_model import SubTaskModel
from app.infrastructure.repositories import SQLAlchemySubTaskRepository


@pytest.mark.asyncio
class TestSQLAlchemySubTaskRepositoryCreate:
    """Unit tests covering the create method behaviour."""

    async def test_create_success(self, repo_db_session):
        """SubTaskを保存でき、DBにも反映されることを確認する。"""
        # Arrange
        repository = SQLAlchemySubTaskRepository(repo_db_session)
        subtask = SubTask.create(
            user_id=1,
            todo_id=1,
            title="Test SubTask",
        )

        # Act
        saved_subtask = await repository.create(subtask)
        await repo_db_session.commit()

        # Assert
        assert saved_subtask.id is not None
        assert saved_subtask.title == "Test SubTask"
        assert saved_subtask.user_id == 1
        assert saved_subtask.todo_id == 1
        assert saved_subtask.is_compleated is False

        result = await repo_db_session.execute(
            select(SubTaskModel).where(SubTaskModel.id == saved_subtask.id)
        )
        model = result.scalar_one()
        assert model.title == "Test SubTask"
        assert model.user_id == 1
        assert model.todo_id == 1
        assert model.is_compleated is False
