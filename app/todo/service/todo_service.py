from fastapi import HTTPException
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.todo.crud.crud_todo import todo as todo_crud
from app.todo.models.todo import Todo as TodoModel
from app.todo.schemas.todo import TodoCreate, TodoPriority, TodoStatus, TodoUpdate


class TodoService:
    """Business logic layer for Todo operations."""

    def get_todo(self, db: Session, todo_id: int) -> TodoModel:
        """Get todo by ID with error handling."""
        db_todo = todo_crud.get(db=db, todo_id=todo_id)
        if not db_todo:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Todo with id {todo_id} not found",
            )
        return db_todo

    def get_todos(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: TodoStatus | None = None,
        priority: TodoPriority | None = None,
    ) -> list[TodoModel]:
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

        return todo_crud.get_multi(
            db=db, skip=skip, limit=limit, status=status, priority=priority
        )

    def create_todo(self, db: Session, todo_in: TodoCreate) -> TodoModel:
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

        return todo_crud.create(db=db, obj_in=todo_in)

    def update_todo(self, db: Session, todo_id: int, todo_in: TodoUpdate) -> TodoModel:
        """Update todo with validation."""
        db_todo = self.get_todo(db=db, todo_id=todo_id)

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

        return todo_crud.update(db=db, db_obj=db_todo, obj_in=todo_in)

    def delete_todo(self, db: Session, todo_id: int) -> TodoModel:
        """Delete todo with validation."""
        db_todo = self.get_todo(db=db, todo_id=todo_id)

        # Business logic: prevent deletion of in-progress todos
        if db_todo.status == TodoStatus.in_progress:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete todo that is in progress. "
                "Complete or cancel it first.",
            )

        deleted_todo = todo_crud.delete(db=db, todo_id=todo_id)
        if not deleted_todo:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Todo with id {todo_id} not found",
            )
        return deleted_todo

    def get_todos_by_status(self, db: Session, status: TodoStatus) -> list[TodoModel]:
        """Get todos by status."""
        return todo_crud.get_by_status(db=db, status=status)

    def get_todo_stats(self, db: Session) -> dict:
        """Get todo statistics."""
        total = todo_crud.count(db=db)
        pending = len(todo_crud.get_by_status(db=db, status=TodoStatus.pending))
        in_progress = len(todo_crud.get_by_status(db=db, status=TodoStatus.in_progress))
        completed = len(todo_crud.get_by_status(db=db, status=TodoStatus.completed))
        canceled = len(todo_crud.get_by_status(db=db, status=TodoStatus.canceled))

        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "canceled": canceled,
        }

    def mark_as_completed(self, db: Session, todo_id: int) -> TodoModel:
        """Mark todo as completed."""
        db_todo = self.get_todo(db=db, todo_id=todo_id)

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
        return todo_crud.update(db=db, db_obj=db_todo, obj_in=todo_update)


todo_service = TodoService()
