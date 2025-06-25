from datetime import datetime

from app.clean.todo.domain.entities.todo import Todo, TodoPriority, TodoStatus
from app.clean.todo.domain.repositories.todo_repository import TodoRepository


class TodoService:
    """Business logic layer for Todo operations.

    This service layer:
    - Contains pure business logic
    - Depends only on Repository Interface (not implementation)
    - Uses Domain Entities exclusively
    - Is completely isolated from database and API concerns
    """

    def __init__(self, repository: TodoRepository):
        self.repository = repository

    def create_todo(
        self,
        title: str,
        description: str | None = None,
        due_date: datetime | None = None,
        priority: TodoPriority = TodoPriority.medium,
        user_id: int | None = None,
    ) -> Todo:
        """Create new todo.

        Note: Basic validation (title length, etc.) is handled by API DTOs.
        This method focuses on business logic only.
        """
        try:
            todo = Todo.create(
                title=title,
                description=description,
                due_date=due_date,
                priority=priority,
            )
            return self.repository.save(todo)
        except Exception as e:
            raise RuntimeError(f"Failed to create todo: {str(e)}") from e

    def get_todo(self, todo_id: int) -> Todo:
        """Get todo by ID with error handling."""
        todo = self.repository.find_by_id(todo_id)
        if not todo:
            raise ValueError(f"Todo with id {todo_id} not found")
        return todo

    def get_todos(
        self,
        skip: int = 0,
        limit: int = 100,
        status: TodoStatus | None = None,
        priority: TodoPriority | None = None,
        user_id: int | None = None,
    ) -> list[Todo]:
        """Get multiple todos with validation."""
        if limit > 1000:
            raise ValueError("Limit cannot exceed 1000")

        if skip < 0:
            raise ValueError("Skip cannot be negative")

        return self.repository.find_with_pagination(
            skip=skip,
            limit=limit,
            status=status,
            priority=priority,
            user_id=user_id,
        )

    def update_todo(
        self,
        todo_id: int,
        title: str | None = None,
        description: str | None = None,
        due_date: datetime | None = None,
        priority: TodoPriority | None = None,
        status: TodoStatus | None = None,
    ) -> Todo:
        """Update todo with business validation."""
        todo = self.get_todo(todo_id)

        if title is not None:
            todo.update_title(title)

        if description is not None:
            todo.update_description(description)

        if due_date is not None:
            todo.update_due_date(due_date)

        if priority is not None:
            todo.update_priority(priority)

        if status is not None:
            if not todo.can_change_status_to(status):
                raise ValueError(f"Cannot change status from {todo.status} to {status}")
            todo.status = status

        return self.repository.save(todo)

    def delete_todo(self, todo_id: int) -> bool:
        """Delete todo with business validation."""
        todo = self.get_todo(todo_id)

        if not todo.can_be_deleted():
            raise ValueError(
                "Cannot delete todo that is in progress. Complete or cancel it first."
            )

        return self.repository.delete(todo_id)

    def complete_todo(self, todo_id: int) -> Todo:
        """Mark todo as completed with business validation."""
        todo = self.get_todo(todo_id)
        todo.mark_completed()
        return self.repository.save(todo)

    def start_todo(self, todo_id: int) -> Todo:
        """Mark todo as in progress."""
        todo = self.get_todo(todo_id)
        todo.mark_in_progress()
        return self.repository.save(todo)

    def cancel_todo(self, todo_id: int) -> Todo:
        """Cancel todo."""
        todo = self.get_todo(todo_id)
        todo.cancel()
        return self.repository.save(todo)

    def get_todos_by_status(
        self, status: TodoStatus, user_id: int | None = None
    ) -> list[Todo]:
        """Get todos by status."""
        return self.repository.find_by_status(status, user_id)

    def get_active_todos(self, user_id: int | None = None) -> list[Todo]:
        """Get active todos (pending or in_progress)."""
        return self.repository.find_active_todos(user_id or 0)

    def get_overdue_todos(self, user_id: int | None = None) -> list[Todo]:
        """Get overdue todos."""
        overdue_todos = self.repository.find_overdue_todos(user_id)
        return [todo for todo in overdue_todos if todo.is_overdue()]

    def get_user_todo_summary(self, user_id: int | None = None) -> dict[str, int]:
        """Get comprehensive todo statistics for a user."""
        total = self.repository.count_total(user_id)
        pending = self.repository.count_by_status(TodoStatus.pending, user_id)
        in_progress = self.repository.count_by_status(TodoStatus.in_progress, user_id)
        completed = self.repository.count_by_status(TodoStatus.completed, user_id)
        canceled = self.repository.count_by_status(TodoStatus.canceled, user_id)

        overdue_count = len(self.get_overdue_todos(user_id))

        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "canceled": canceled,
            "overdue": overdue_count,
            "active": pending + in_progress,
        }

    def get_todos_by_priority(
        self, priority: TodoPriority, user_id: int | None = None
    ) -> list[Todo]:
        """Get todos by priority."""
        return self.repository.find_by_priority(priority, user_id)

    def get_high_priority_todos(self, user_id: int | None = None) -> list[Todo]:
        """Get high priority todos that are active."""
        high_priority_todos = self.repository.find_by_priority(
            TodoPriority.high, user_id
        )
        return [
            todo
            for todo in high_priority_todos
            if todo.status in [TodoStatus.pending, TodoStatus.in_progress]
        ]

    def bulk_update_status(
        self, todo_ids: list[int], new_status: TodoStatus
    ) -> list[Todo]:
        """Update status for multiple todos."""
        updated_todos = []

        for todo_id in todo_ids:
            try:
                todo = self.get_todo(todo_id)
                if todo.can_change_status_to(new_status):
                    todo.status = new_status
                    updated_todo = self.repository.save(todo)
                    updated_todos.append(updated_todo)
            except (ValueError, RuntimeError):
                continue

        return updated_todos

    def bulk_delete_completed_todos(self, user_id: int | None = None) -> int:
        """Delete all completed todos for a user."""
        completed_todos = self.repository.find_by_status(TodoStatus.completed, user_id)
        deleted_count = 0

        for todo in completed_todos:
            if todo.id is not None and self.repository.delete(todo.id):
                deleted_count += 1

        return deleted_count
