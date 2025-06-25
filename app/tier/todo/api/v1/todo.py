from fastapi import APIRouter, Depends, Query

from app.tier.todo.schemas.todo import (
    Todo,
    TodoCreate,
    TodoPriority,
    TodoStatus,
    TodoUpdate,
)
from app.tier.todo.service.todo_service import TodoService, getTodoService

router = APIRouter()


@router.get("/", response_model=list[Todo])
def get_todos(
    skip: int = Query(0, ge=0, description="Number of todos to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of todos to return"),
    status: TodoStatus | None = Query(None, description="Filter by status"),
    priority: TodoPriority | None = Query(None, description="Filter by priority"),
    service: TodoService = Depends(getTodoService),
):
    """Get all todos with optional filtering."""
    return service.get_todos(skip=skip, limit=limit, status=status, priority=priority)


@router.post("/", response_model=Todo, status_code=201)
def create_todo(
    todo_in: TodoCreate,
    service: TodoService = Depends(getTodoService),
):
    """Create a new todo."""
    return service.create_todo(todo_in=todo_in)


@router.get("/{todo_id}", response_model=Todo)
def get_todo(
    todo_id: int,
    service: TodoService = Depends(getTodoService),
):
    """Get a specific todo by ID."""
    return service.get_todo(todo_id=todo_id)


@router.put("/{todo_id}", response_model=Todo)
def update_todo(
    todo_id: int,
    todo_in: TodoUpdate,
    service: TodoService = Depends(getTodoService),
):
    """Update a specific todo."""
    return service.update_todo(todo_id=todo_id, todo_in=todo_in)


@router.delete("/{todo_id}", response_model=Todo)
def delete_todo(
    todo_id: int,
    service: TodoService = Depends(getTodoService),
):
    """Delete a specific todo."""
    return service.delete_todo(todo_id=todo_id)


@router.patch("/{todo_id}/complete", response_model=Todo)
def mark_todo_completed(
    todo_id: int,
    service: TodoService = Depends(getTodoService),
):
    """Mark a todo as completed."""
    return service.mark_as_completed(todo_id=todo_id)


@router.get("/status/{status}", response_model=list[Todo])
def get_todos_by_status(
    status: TodoStatus,
    service: TodoService = Depends(getTodoService),
):
    """Get todos by status."""
    return service.get_todos_by_status(status=status)


@router.get("/stats/summary")
def get_todo_stats(
    service: TodoService = Depends(getTodoService),
):
    """Get todo statistics summary."""
    return service.get_todo_stats()
