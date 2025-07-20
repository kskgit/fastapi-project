from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.domain.entities.todo import Todo, TodoPriority, TodoStatus
from app.domain.repositories.todo_repository import TodoRepository
from app.infrastructure.database.models import TodoModel


class SQLAlchemyTodoRepository(TodoRepository):
    """SQLAlchemy implementation of TodoRepository.

    Handles all database-specific concerns including:
    - SQLAlchemy model ↔ Domain entity conversion
    - Query optimization and lazy loading prevention
    - Transaction management
    - Error handling (SQLAlchemy exceptions → domain exceptions)
    """

    def __init__(self, db: Session):
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

    def save(self, todo: Todo) -> Todo:
        """Save a todo (create or update)."""
        try:
            if todo.id is None:
                model = TodoModel(
                    title=todo.title,
                    user_id=todo.user_id,
                    description=todo.description,
                    due_date=todo.due_date,
                    status=todo.status,
                    priority=todo.priority,
                )
                self.db.add(model)
            else:
                existing_model = (
                    self.db.query(TodoModel).filter(TodoModel.id == todo.id).first()
                )
                if not existing_model:
                    raise ValueError(f"Todo with id {todo.id} not found")

                existing_model.title = todo.title
                existing_model.user_id = todo.user_id
                existing_model.description = todo.description
                existing_model.due_date = todo.due_date
                existing_model.status = todo.status
                existing_model.priority = todo.priority
                model = existing_model

            self.db.commit()
            self.db.refresh(model)
            return self._to_domain_entity(model)

        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Database error while saving todo: {str(e)}")

    def find_by_id(self, todo_id: int) -> Todo | None:
        """Find todo by ID."""
        try:
            model = self.db.query(TodoModel).filter(TodoModel.id == todo_id).first()
            return self._to_domain_entity(model) if model else None
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while finding todo: {str(e)}")

    def find_all_by_user_id(self, user_id: int) -> list[Todo]:
        """Find all todos for a specific user.

        Note: Current implementation doesn't include user filtering.
        This method is prepared for future user-based filtering.
        """
        try:
            models = self.db.query(TodoModel).all()
            return [self._to_domain_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while finding todos: {str(e)}")

    def find_active_todos(self, user_id: int) -> list[Todo]:
        """Find active todos (pending or in_progress) for a user."""
        try:
            models = (
                self.db.query(TodoModel)
                .filter(
                    TodoModel.status.in_([TodoStatus.pending, TodoStatus.in_progress])
                )
                .all()
            )
            return [self._to_domain_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while finding active todos: {str(e)}")

    def find_by_status(self, status: TodoStatus, user_id: int) -> list[Todo]:
        """Find todos by status."""
        try:
            models = (
                self.db.query(TodoModel)
                .filter(and_(TodoModel.status == status, TodoModel.user_id == user_id))
                .all()
            )
            return [self._to_domain_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Database error while finding todos by status: {str(e)}"
            )

    def find_by_priority(self, priority: TodoPriority, user_id: int) -> list[Todo]:
        """Find todos by priority."""
        try:
            models = (
                self.db.query(TodoModel)
                .filter(
                    and_(TodoModel.priority == priority, TodoModel.user_id == user_id)
                )
                .all()
            )
            return [self._to_domain_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Database error while finding todos by priority: {str(e)}"
            )

    def find_overdue_todos(self, user_id: int) -> list[Todo]:
        """Find overdue todos."""
        try:
            current_time = datetime.now()
            models = (
                self.db.query(TodoModel)
                .filter(
                    and_(
                        TodoModel.due_date < current_time,
                        TodoModel.status.in_(
                            [TodoStatus.pending, TodoStatus.in_progress]
                        ),
                    )
                )
                .all()
            )
            return [self._to_domain_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while finding overdue todos: {str(e)}")

    def find_with_pagination(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: TodoStatus | None = None,
        priority: TodoPriority | None = None,
    ) -> list[Todo]:
        """Find todos with pagination and optional filters."""
        try:
            query = self.db.query(TodoModel)

            filters = [TodoModel.user_id == user_id]
            if status:
                filters.append(TodoModel.status == status)
            if priority:
                filters.append(TodoModel.priority == priority)

            query = query.filter(and_(*filters))

            models = query.offset(skip).limit(limit).all()
            return [self._to_domain_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Database error while finding todos with pagination: {str(e)}"
            )

    def delete(self, todo_id: int) -> bool:
        """Delete todo by ID."""
        try:
            model = self.db.query(TodoModel).filter(TodoModel.id == todo_id).first()
            if not model:
                return False

            self.db.delete(model)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Database error while deleting todo: {str(e)}")

    def count_by_status(self, status: TodoStatus, user_id: int) -> int:
        """Count todos by status."""
        try:
            return (
                self.db.query(TodoModel)
                .filter(and_(TodoModel.status == status, TodoModel.user_id == user_id))
                .count()
            )
        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Database error while counting todos by status: {str(e)}"
            )

    def count_total(self, user_id: int) -> int:
        """Count total todos."""
        try:
            return self.db.query(TodoModel).filter(TodoModel.user_id == user_id).count()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while counting total todos: {str(e)}")

    def exists(self, todo_id: int) -> bool:
        """Check if todo exists."""
        try:
            return (
                self.db.query(TodoModel.id).filter(TodoModel.id == todo_id).first()
                is not None
            )
        except SQLAlchemyError as e:
            raise RuntimeError(
                f"Database error while checking todo existence: {str(e)}"
            )
