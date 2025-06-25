from fastapi import Depends, HTTPException
from fastapi import status as http_status

from app.tier.todo.crud.crud_todo import TodoCRUDInterface, getTodoCRID
from app.tier.todo.schemas.todo import (
    Todo,
    TodoCreate,
    TodoPriority,
    TodoStatus,
    TodoUpdate,
)


class TodoService:
    """Business logic layer for Todo operations."""

    def __init__(self, crud: TodoCRUDInterface):
        self.crud = crud

    def get_todo(self, todo_id: int) -> Todo:
        """Get todo by ID with error handling."""
        db_todo = self.crud.get(todo_id=todo_id)
        if not db_todo:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Todo with id {todo_id} not found",
            )
        return db_todo

    def get_todos(
        self,
        skip: int = 0,
        limit: int = 100,
        status: TodoStatus | None = None,
        priority: TodoPriority | None = None,
    ) -> list[Todo]:
        """Get multiple todos with validation."""
        if limit > 1000:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Limit cannot exceed 1000",
            )

        if skip < 0:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Skip cannot be negative",
            )

        return self.crud.get_multi(
            skip=skip, limit=limit, status=status, priority=priority
        )

    def create_todo(self, todo_in: TodoCreate) -> Todo:
        """Create new todo with validation."""
        # Business logic: validate title length
        if len(todo_in.title.strip()) < 3:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Title must be at least 3 characters long",
            )

        # Business logic: validate description length if provided
        if todo_in.description and len(todo_in.description) > 500:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Description cannot exceed 500 characters",
            )

        return self.crud.create(obj_in=todo_in)

    def update_todo(self, todo_id: int, todo_in: TodoUpdate) -> Todo:
        """Update todo with validation."""
        db_todo = self.get_todo(todo_id=todo_id)

        # Business logic: validate title if being updated
        if todo_in.title is not None and len(todo_in.title.strip()) < 3:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Title must be at least 3 characters long",
            )

        # Business logic: validate description if being updated
        if todo_in.description is not None and len(todo_in.description) > 500:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Description cannot exceed 500 characters",
            )

        # Business logic: prevent updating completed todos to pending
        if (
            db_todo.status == TodoStatus.completed
            and todo_in.status == TodoStatus.pending
        ):
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Cannot change completed todo back to pending",
            )

        return self.crud.update(db_obj=db_todo, obj_in=todo_in)

    def delete_todo(self, todo_id: int) -> Todo:
        """Delete todo with validation."""
        db_todo = self.get_todo(todo_id=todo_id)

        # Business logic: prevent deletion of in-progress todos
        if db_todo.status == TodoStatus.in_progress:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete todo that is in progress. "
                "Complete or cancel it first.",
            )

        deleted_todo = self.crud.delete(todo_id=todo_id)
        if not deleted_todo:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Todo with id {todo_id} not found",
            )
        return deleted_todo

    def get_todos_by_status(self, status: TodoStatus) -> list[Todo]:
        """Get todos by status."""
        return self.crud.get_by_status(status=status)

    def get_todo_stats(self) -> dict:
        """Get todo statistics."""
        total = self.crud.count()
        pending = len(self.crud.get_by_status(status=TodoStatus.pending))
        in_progress = len(self.crud.get_by_status(status=TodoStatus.in_progress))
        completed = len(self.crud.get_by_status(status=TodoStatus.completed))
        canceled = len(self.crud.get_by_status(status=TodoStatus.canceled))

        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "canceled": canceled,
        }

    def mark_as_completed(self, todo_id: int) -> Todo:
        """Mark todo as completed."""
        db_todo = self.get_todo(todo_id=todo_id)

        if db_todo.status == TodoStatus.completed:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Todo is already completed",
            )

        if db_todo.status == TodoStatus.canceled:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Cannot complete a canceled todo",
            )

        todo_update = TodoUpdate(status=TodoStatus.completed)
        return self.crud.update(db_obj=db_todo, obj_in=todo_update)


def getTodoService(crud: TodoCRUDInterface = Depends(getTodoCRID)) -> TodoService:
    return TodoService(crud)
