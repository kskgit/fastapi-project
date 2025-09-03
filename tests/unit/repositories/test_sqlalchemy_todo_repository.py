"""Unit tests for SQLAlchemyTodoRepository."""

import pytest

from app.domain.entities.todo import Todo, TodoPriority, TodoStatus
from app.infrastructure.repositories.sqlalchemy_todo_repository import (
    SQLAlchemyTodoRepository,
)


@pytest.mark.asyncio
class TestSQLAlchemyTodoRepository:
    """Unit tests for SQLAlchemyTodoRepository implementation."""

    async def test_save_creates_todo_in_database(self, repo_db_session):
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

        # Assert - Todo exists in database
        found_todo = await repository.find_by_id(saved_todo.id)
        assert found_todo is not None
        assert found_todo.id == saved_todo.id
        assert found_todo.title == "Test Todo"
        assert found_todo.description == "Test Description"
        assert found_todo.user_id == 1
        assert found_todo.priority == TodoPriority.high
