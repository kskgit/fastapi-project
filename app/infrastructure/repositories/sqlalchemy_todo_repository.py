"""SQLAlchemy implementation of TodoRepository."""

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.todo import Todo, TodoPriority, TodoStatus
from app.domain.exceptions.system import DataPersistenceException
from app.domain.repositories.todo_repository import TodoRepository
from app.infrastructure.database.models import TodoModel


class SQLAlchemyTodoRepository(TodoRepository):
    """SQLAlchemy implementation of TodoRepository.

    Handles database operations using SQLAlchemy ORM with async/await support.
    Converts between domain entities and SQLAlchemy models.
    """

    def __init__(self, db: AsyncSession):
        """Initialize with database session.

        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    def _to_domain_entity(self, model: TodoModel) -> Todo:
        """Convert SQLAlchemy model to domain entity."""
        return Todo(
            id=model.id,
            title=model.title,
            user_id=model.user_id,
            description=model.description,
            due_date=model.due_date,
            status=model.status,
            priority=model.priority,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Todo) -> TodoModel:
        """Convert domain entity to SQLAlchemy model."""
        return TodoModel(
            id=entity.id,
            title=entity.title,
            user_id=entity.user_id,
            description=entity.description,
            due_date=entity.due_date,
            status=entity.status,
            priority=entity.priority,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def save(self, todo: Todo) -> Todo:
        """Save a todo (create or update).

        Note: Transaction management is handled by the UseCase layer.
        Always flushes to ensure ID is available for return value.
        """
        try:
            if todo.id is None:
                # Create new todo
                model = self._to_model(todo)
                model.created_at = datetime.now()
                model.updated_at = datetime.now()
                self.db.add(model)
                await self.db.flush()
                await self.db.refresh(model)
            else:
                # Update existing todo
                result = await self.db.execute(
                    select(TodoModel).where(TodoModel.id == todo.id)
                )
                model_or_none = result.scalar_one_or_none()
                if model_or_none is None:
                    raise ValueError(f"Todo with id {todo.id} not found")
                model = model_or_none

                # Update fields
                model.title = todo.title
                model.description = todo.description
                model.due_date = todo.due_date
                model.status = todo.status
                model.priority = todo.priority
                model.updated_at = datetime.now()
                await self.db.flush()
                await self.db.refresh(model)

            return self._to_domain_entity(model)

        except SQLAlchemyError as e:
            raise DataPersistenceException(
                message=f"Failed to save todo: {str(e)}",
                operation="save",
                entity_type="todo",
                entity_id=todo.id if todo.id else None,
            )

    async def find_by_id(self, todo_id: int) -> Todo | None:
        """Find todo by ID."""
        try:
            result = await self.db.execute(
                select(TodoModel).where(TodoModel.id == todo_id)
            )
            model = result.scalar_one_or_none()
            return self._to_domain_entity(model) if model else None

        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while finding todo by id: {str(e)}")

    async def find_all_by_user_id(self, user_id: int) -> list[Todo]:
        """Find all todos for a specific user."""
        try:
            result = await self.db.execute(
                select(TodoModel).where(TodoModel.user_id == user_id)
            )
            models: Sequence[TodoModel] = result.scalars().all()
            return [self._to_domain_entity(model) for model in models]

        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while finding todos by user: {str(e)}")

    async def find_active_todos(self, user_id: int) -> list[Todo]:
        """Find active todos (pending or in_progress) for a user."""
        try:
            result = await self.db.execute(
                select(TodoModel).where(
                    TodoModel.user_id == user_id,
                    TodoModel.status.in_([TodoStatus.pending, TodoStatus.in_progress]),
                )
            )
            models: Sequence[TodoModel] = result.scalars().all()
            return [self._to_domain_entity(model) for model in models]

        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while finding active todos: {str(e)}")

    async def find_by_status(self, status: TodoStatus, user_id: int) -> list[Todo]:
        """Find todos by status for a specific user."""
        try:
            result = await self.db.execute(
                select(TodoModel).where(
                    TodoModel.user_id == user_id, TodoModel.status == status
                )
            )
            models: Sequence[TodoModel] = result.scalars().all()
            return [self._to_domain_entity(model) for model in models]

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Database error while finding todos by status: {str(e)}"
            )

    async def find_by_priority(
        self, priority: TodoPriority, user_id: int
    ) -> list[Todo]:
        """Find todos by priority for a specific user."""
        try:
            result = await self.db.execute(
                select(TodoModel).where(
                    TodoModel.user_id == user_id, TodoModel.priority == priority
                )
            )
            models: Sequence[TodoModel] = result.scalars().all()
            return [self._to_domain_entity(model) for model in models]

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Database error while finding todos by priority: {str(e)}"
            )

    async def find_overdue_todos(self, user_id: int) -> list[Todo]:
        """Find overdue todos for a specific user."""
        try:
            now = datetime.now()
            result = await self.db.execute(
                select(TodoModel).where(
                    TodoModel.user_id == user_id,
                    TodoModel.due_date < now,
                    TodoModel.status != TodoStatus.completed,
                )
            )
            models: Sequence[TodoModel] = result.scalars().all()
            return [self._to_domain_entity(model) for model in models]

        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while finding overdue todos: {str(e)}")

    async def find_with_pagination(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: TodoStatus | None = None,
        priority: TodoPriority | None = None,
    ) -> list[Todo]:
        """Find todos with pagination and optional filters for a specific user."""
        try:
            query = select(TodoModel).where(TodoModel.user_id == user_id)

            if status:
                query = query.where(TodoModel.status == status)
            if priority:
                query = query.where(TodoModel.priority == priority)

            query = query.offset(skip).limit(limit)

            result = await self.db.execute(query)
            models: Sequence[TodoModel] = result.scalars().all()
            return [self._to_domain_entity(model) for model in models]

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Database error while finding todos with pagination: {str(e)}"
            )

    async def delete(self, todo_id: int) -> bool:
        """Delete todo by ID.

        Note: Transaction management is handled by the UseCase layer.
        """
        try:
            result = await self.db.execute(
                select(TodoModel).where(TodoModel.id == todo_id)
            )
            model = result.scalar_one_or_none()

            if model is None:
                return False

            await self.db.delete(model)
            return True

        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while deleting todo: {str(e)}")

    async def count_by_status(self, status: TodoStatus, user_id: int) -> int:
        """Count todos by status for a specific user."""
        try:
            from sqlalchemy import func

            result = await self.db.execute(
                select(func.count(TodoModel.id)).where(
                    TodoModel.user_id == user_id, TodoModel.status == status
                )
            )
            return result.scalar() or 0

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Database error while counting todos by status: {str(e)}"
            )

    async def count_total(self, user_id: int) -> int:
        """Count total todos for a specific user."""
        try:
            from sqlalchemy import func

            result = await self.db.execute(
                select(func.count(TodoModel.id)).where(TodoModel.user_id == user_id)
            )
            return result.scalar() or 0

        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while counting total todos: {str(e)}")

    async def exists(self, todo_id: int) -> bool:
        """Check if todo exists."""
        try:
            result = await self.db.execute(
                select(TodoModel.id).where(TodoModel.id == todo_id)
            )
            return result.scalar_one_or_none() is not None

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Database error while checking todo existence: {str(e)}"
            )

    async def delete_all_by_user_id(self, user_id: int) -> int:
        """Delete all todos for a specific user.

        Note: Transaction management is handled by the UseCase layer.
        """
        try:
            from sqlalchemy import delete

            # Count todos before deletion for return value
            count_result = await self.db.execute(
                select(TodoModel).where(TodoModel.user_id == user_id)
            )
            todos_to_delete = count_result.scalars().all()
            delete_count = len(todos_to_delete)

            if delete_count > 0:
                # Execute bulk delete
                await self.db.execute(
                    delete(TodoModel).where(TodoModel.user_id == user_id)
                )

            return delete_count

        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Database error while deleting todos for user {user_id}: {str(e)}"
            )
