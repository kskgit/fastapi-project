"""Tests for SQLAlchemyTodoRepository.create."""

import pytest
from sqlalchemy import select

from app.domain.entities import Todo, TodoPriority, TodoStatus
from app.domain.exceptions import DataOperationException
from app.infrastructure.database.models import TodoModel
from app.infrastructure.repositories import SQLAlchemyTodoRepository


@pytest.mark.asyncio
class TestSQLAlchemyTodoRepositoryCreate:
    """Unit tests covering the create method behaviour."""

    async def test_create_success(self, repo_db_session):
        """Todoを保存でき、DBにも反映されることを確認する。"""
        # Arrange
        repository = SQLAlchemyTodoRepository(repo_db_session)
        todo = Todo.create(
            user_id=1,
            title="Test Todo",
            description="Test Description",
            priority=TodoPriority.high,
        )

        # Act
        saved_todo = await repository.create(todo)
        await repo_db_session.commit()

        # Assert
        assert saved_todo.id is not None
        assert saved_todo.title == "Test Todo"
        assert saved_todo.description == "Test Description"
        assert saved_todo.user_id == 1
        assert saved_todo.priority == TodoPriority.high
        assert saved_todo.status == TodoStatus.pending
        assert saved_todo.created_at is not None
        assert saved_todo.updated_at is not None

        result = await repo_db_session.execute(
            select(TodoModel).where(TodoModel.id == saved_todo.id)
        )
        model = result.scalar_one()
        assert model.title == "Test Todo"
        assert model.description == "Test Description"
        assert model.user_id == 1
        assert model.priority == TodoPriority.high

    async def test_create_failure_raises_data_operation_exception(
        self, repo_db_session_sqlalchemy_error
    ):
        """SQLAlchemyError を DataOperationException にラップすることを確認する。"""
        # Arrange
        repository = SQLAlchemyTodoRepository(repo_db_session_sqlalchemy_error)
        todo = Todo.create(
            user_id=1,
            title="Bad Todo",
            description="Fails on flush",
            priority=TodoPriority.medium,
        )

        # Act / Assert
        with pytest.raises(DataOperationException) as exc_info:
            await repository.create(todo)

        assert exc_info.value.details["operation_context"] == (
            "SQLAlchemyTodoRepository.create"
        )
