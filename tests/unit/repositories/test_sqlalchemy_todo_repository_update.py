"""Tests for SQLAlchemyTodoRepository.update."""

import pytest
from sqlalchemy import select

from app.domain.entities.todo import Todo, TodoPriority, TodoStatus
from app.domain.exceptions.business import TodoNotFoundException
from app.domain.exceptions.system import DataOperationException
from app.infrastructure.database.models import TodoModel
from app.infrastructure.repositories.sqlalchemy_todo_repository import (
    SQLAlchemyTodoRepository,
)


@pytest.mark.asyncio
class TestSQLAlchemyTodoRepositoryUpdate:
    """Unit tests covering the update method behaviour."""

    async def test_update_success(self, repo_db_session):
        """既存Todoを更新し、DBにも反映されることを確認する。"""
        # Arrange
        repository = SQLAlchemyTodoRepository(repo_db_session)
        existing = await repository.create(
            Todo.create(
                user_id=1,
                title="Original",
                description="Desc",
                priority=TodoPriority.medium,
            )
        )

        updated_todo = Todo(
            id=existing.id,
            user_id=existing.user_id,
            title="Updated",
            description="New Description",
            due_date=existing.due_date,
            status=TodoStatus.in_progress,
            priority=TodoPriority.high,
            created_at=existing.created_at,
            updated_at=existing.updated_at,
        )

        # Act
        result = await repository.update(updated_todo)
        await repo_db_session.commit()

        # Assert
        assert result.id == existing.id
        assert result.title == "Updated"
        assert result.description == "New Description"
        assert result.status == TodoStatus.in_progress
        assert result.priority == TodoPriority.high

        db_result = await repo_db_session.execute(
            select(TodoModel).where(TodoModel.id == existing.id)
        )
        model = db_result.scalar_one()
        assert model.title == "Updated"
        assert model.description == "New Description"
        assert model.status == TodoStatus.in_progress
        assert model.priority == TodoPriority.high

    async def test_update_failure_not_found(self, repo_db_session):
        """存在しないTodoの場合にTodoNotFoundExceptionを送出する。"""
        # Arrange
        repository = SQLAlchemyTodoRepository(repo_db_session)
        missing = Todo(
            id=999,
            user_id=1,
            title="Missing",
            description="Should fail",
            status=TodoStatus.pending,
            priority=TodoPriority.low,
        )

        # Act / Assert
        with pytest.raises(TodoNotFoundException) as exc_info:
            await repository.update(missing)

        assert str(exc_info.value) == "Todo with id 999 not found"

    async def test_update_failure_raises_data_operation_exception(
        self, repo_db_session, repo_db_session_sqlalchemy_error
    ):
        """SQLAlchemyError が DataOperationException にラップされることを確認する。"""
        # Arrange
        repository = SQLAlchemyTodoRepository(repo_db_session)
        existing = await repository.create(
            Todo.create(
                user_id=1,
                title="Original",
                description="Desc",
                priority=TodoPriority.low,
            )
        )
        await repo_db_session.commit()

        error_repository = SQLAlchemyTodoRepository(repo_db_session_sqlalchemy_error)
        updated = Todo(
            id=existing.id,
            user_id=existing.user_id,
            title="Broken",
            description="Desc",
            status=TodoStatus.pending,
            priority=TodoPriority.low,
        )

        # Act / Assert
        with pytest.raises(DataOperationException) as exc_info:
            await error_repository.update(updated)

        assert exc_info.value.details["operation_context"] == (
            "SQLAlchemyTodoRepository.update"
        )
