"""Unit tests for SQLAlchemyTodoRepository."""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.domain.entities.todo import Todo, TodoPriority, TodoStatus
from app.domain.exceptions.system import DataOperationException
from app.infrastructure.database.models import TodoModel
from app.infrastructure.repositories.sqlalchemy_todo_repository import (
    SQLAlchemyTodoRepository,
)


@pytest.mark.asyncio
class TestSQLAlchemyTodoRepository:
    """Unit tests for SQLAlchemyTodoRepository implementation."""

    async def test_create_success(self, repo_db_session):
        """Test that create persists a new Todo."""
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

    async def test_create_failure_raises_data_operation_exception(
        self, repo_db_session, monkeypatch
    ):
        """Test that SQL errors are wrapped in DataOperationException."""
        # Arrange
        repository = SQLAlchemyTodoRepository(repo_db_session)
        todo = Todo.create(
            user_id=1,
            title="Bad Todo",
            description="Fails on flush",
            priority=TodoPriority.medium,
        )

        async def _raise_sqlalchemy_error(*args, **kwargs):
            raise SQLAlchemyError("flush failed")

        monkeypatch.setattr(repo_db_session, "flush", _raise_sqlalchemy_error)

        # Act
        with pytest.raises(DataOperationException) as exc_info:
            await repository.create(todo)

        # Assert
        assert exc_info.value.details["operation_context"] == (
            "SQLAlchemyTodoRepository.create"
        )

    async def test_update_success(self, repo_db_session):
        """Test that update modifies an existing Todo."""
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

        # Assert - Returned todo reflects updates
        assert result.id == existing.id
        assert result.title == "Updated"
        assert result.description == "New Description"
        assert result.status == TodoStatus.in_progress
        assert result.priority == TodoPriority.high

        # Assert - Database row is updated
        db_result = await repo_db_session.execute(
            select(TodoModel).where(TodoModel.id == existing.id)
        )
        model = db_result.scalar_one()
        assert model.title == "Updated"
        assert model.description == "New Description"
        assert model.status == TodoStatus.in_progress
        assert model.priority == TodoPriority.high

    async def test_update_failure_raises_data_operation_exception(
        self, repo_db_session, monkeypatch
    ):
        """Update wraps SQLAlchemy errors in DataOperationException."""
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

        async def _raise_sqlalchemy_error(*args, **kwargs):
            raise SQLAlchemyError("flush failed")

        monkeypatch.setattr(repo_db_session, "flush", _raise_sqlalchemy_error)

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
            await repository.update(updated)

        # Assert
        assert exc_info.value.details["operation_context"] == (
            "SQLAlchemyTodoRepository.update"
        )

    async def test_find_by_id_failure_not_found(self, repo_db_session):
        """Test that find_by_id returns None when todo does not exist."""
        # Arrange
        repository = SQLAlchemyTodoRepository(repo_db_session)

        # Act
        result = await repository.find_by_id(999)

        # Assert
        assert result is None
