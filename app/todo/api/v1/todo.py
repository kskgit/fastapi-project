from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.todo.schemas.todo import Todo, TodoCreate, TodoPriority, TodoStatus, TodoUpdate
from app.todo.service.todo_service import todo_service

router = APIRouter()


@router.get("/", response_model=list[Todo])
def get_todos(
    skip: int = Query(0, ge=0, description="Number of todos to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of todos to return"),
    status: TodoStatus | None = Query(None, description="Filter by status"),
    priority: TodoPriority | None = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db),
):
    """Get all todos with optional filtering."""
    return todo_service.get_todos(
        db=db, skip=skip, limit=limit, status=status, priority=priority
    )


@router.post("/", response_model=Todo, status_code=201)
def create_todo(
    todo_in: TodoCreate,
    db: Session = Depends(get_db),
):
    """Create a new todo."""
    return todo_service.create_todo(db=db, todo_in=todo_in)


@router.get("/{todo_id}", response_model=Todo)
def get_todo(
    todo_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific todo by ID."""
    return todo_service.get_todo(db=db, todo_id=todo_id)


@router.put("/{todo_id}", response_model=Todo)
def update_todo(
    todo_id: int,
    todo_in: TodoUpdate,
    db: Session = Depends(get_db),
):
    """Update a specific todo."""
    return todo_service.update_todo(db=db, todo_id=todo_id, todo_in=todo_in)


@router.delete("/{todo_id}", response_model=Todo)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
):
    """Delete a specific todo."""
    return todo_service.delete_todo(db=db, todo_id=todo_id)


@router.patch("/{todo_id}/complete", response_model=Todo)
def mark_todo_completed(
    todo_id: int,
    db: Session = Depends(get_db),
):
    """Mark a todo as completed."""
    return todo_service.mark_as_completed(db=db, todo_id=todo_id)


@router.get("/status/{status}", response_model=list[Todo])
def get_todos_by_status(
    status: TodoStatus,
    db: Session = Depends(get_db),
):
    """Get todos by status."""
    return todo_service.get_todos_by_status(db=db, status=status)


@router.get("/stats/summary")
def get_todo_stats(
    db: Session = Depends(get_db),
):
    """Get todo statistics summary."""
    return todo_service.get_todo_stats(db=db)
