"""Unit tests for SQLAlchemyTodoRepository."""

import pytest
from sqlalchemy import select

from app.domain.entities.todo import Todo, TodoPriority, TodoStatus
from app.infrastructure.database.models import TodoModel
from app.infrastructure.repositories.sqlalchemy_todo_repository import (
    SQLAlchemyTodoRepository,
)


@pytest.mark.asyncio
class TestSQLAlchemyTodoRepository:
    """Unit tests for SQLAlchemyTodoRepository implementation."""

    async def test_save_success(self, repo_db_session):
        """Test that save method creates a Todo in the database."""
        # Arrange
        repository = SQLAlchemyTodoRepository(repo_db_session)
        todo = Todo.create(
            user_id=1,
            title="Test Todo",
            description="Test Description",
            priority=TodoPriority.high,
        )

        # Act
        saved_todo = await repository.save(todo)
        await repo_db_session.commit()

        # Assert - Returned todo has ID and correct data
        assert saved_todo.id is not None
        assert saved_todo.title == "Test Todo"
        assert saved_todo.description == "Test Description"
        assert saved_todo.user_id == 1
        assert saved_todo.priority == TodoPriority.high
        assert saved_todo.status == TodoStatus.pending
        assert saved_todo.created_at is not None
        assert saved_todo.updated_at is not None

        # Assert - Todo exists in database (direct DB check)
        result = await repo_db_session.execute(
            select(TodoModel).where(TodoModel.id == saved_todo.id)
        )
        model = result.scalar_one()
        assert model.title == "Test Todo"
        assert model.description == "Test Description"
        assert model.user_id == 1
        assert model.priority == TodoPriority.high
