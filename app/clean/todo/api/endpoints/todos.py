from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status as http_status

from app.clean.todo.api.dtos.todo_dto import (
    BulkUpdateDTO,
    TodoCreateDTO,
    TodoResponseDTO,
    TodoSummaryDTO,
    TodoUpdateDTO,
)
from app.clean.todo.domain.entities.todo import TodoPriority, TodoStatus
from app.clean.todo.services.todo_service import TodoService


def get_todo_service() -> TodoService:
    """Dependency to get TodoService instance.

    This will be overridden by dependency injection in main.py.
    """
    raise NotImplementedError("Dependency injection not configured")


router = APIRouter(prefix="/api/v1/todos", tags=["todos"])


@router.get("/", response_model=list[TodoResponseDTO])
async def get_todos(
    skip: int = Query(0, ge=0, description="Number of todos to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of todos to return"),
    status: TodoStatus | None = Query(None, description="Filter by status"),
    priority: TodoPriority | None = Query(None, description="Filter by priority"),
    service: TodoService = Depends(get_todo_service),
) -> list[TodoResponseDTO]:
    """Get all todos with optional filtering."""
    todos = service.get_todos(skip=skip, limit=limit, status=status, priority=priority)
    return [TodoResponseDTO.from_domain_entity(todo) for todo in todos]


@router.post(
    "/", response_model=TodoResponseDTO, status_code=http_status.HTTP_201_CREATED
)
async def create_todo(
    todo_data: TodoCreateDTO,
    service: TodoService = Depends(get_todo_service),
) -> TodoResponseDTO:
    """Create a new todo."""
    todo = service.create_todo(
        title=todo_data.title,
        description=todo_data.description,
        due_date=todo_data.due_date,
        priority=todo_data.priority,
    )
    return TodoResponseDTO.from_domain_entity(todo)


@router.get("/{todo_id}", response_model=TodoResponseDTO)
async def get_todo(
    todo_id: int,
    service: TodoService = Depends(get_todo_service),
) -> TodoResponseDTO:
    """Get a specific todo by ID."""
    todo = service.get_todo(todo_id)
    return TodoResponseDTO.from_domain_entity(todo)


@router.put("/{todo_id}", response_model=TodoResponseDTO)
async def update_todo(
    todo_id: int,
    todo_data: TodoUpdateDTO,
    service: TodoService = Depends(get_todo_service),
) -> TodoResponseDTO:
    """Update a specific todo."""
    todo = service.update_todo(
        todo_id=todo_id,
        title=todo_data.title,
        description=todo_data.description,
        due_date=todo_data.due_date,
        priority=todo_data.priority,
        status=todo_data.status,
    )
    return TodoResponseDTO.from_domain_entity(todo)


@router.delete("/{todo_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    service: TodoService = Depends(get_todo_service),
) -> None:
    """Delete a specific todo."""
    deleted = service.delete_todo(todo_id)
    if not deleted:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Todo with id {todo_id} not found",
        )


@router.patch("/{todo_id}/complete", response_model=TodoResponseDTO)
async def complete_todo(
    todo_id: int,
    service: TodoService = Depends(get_todo_service),
) -> TodoResponseDTO:
    """Mark a todo as completed."""
    todo = service.complete_todo(todo_id)
    return TodoResponseDTO.from_domain_entity(todo)


@router.patch("/{todo_id}/start", response_model=TodoResponseDTO)
async def start_todo(
    todo_id: int,
    service: TodoService = Depends(get_todo_service),
) -> TodoResponseDTO:
    """Mark a todo as in progress."""
    todo = service.start_todo(todo_id)
    return TodoResponseDTO.from_domain_entity(todo)


@router.patch("/{todo_id}/cancel", response_model=TodoResponseDTO)
async def cancel_todo(
    todo_id: int,
    service: TodoService = Depends(get_todo_service),
) -> TodoResponseDTO:
    """Cancel a todo."""
    todo = service.cancel_todo(todo_id)
    return TodoResponseDTO.from_domain_entity(todo)


@router.get("/status/{status}", response_model=list[TodoResponseDTO])
async def get_todos_by_status(
    status: TodoStatus,
    service: TodoService = Depends(get_todo_service),
) -> list[TodoResponseDTO]:
    """Get todos by status."""
    todos = service.get_todos_by_status(status)
    return [TodoResponseDTO.from_domain_entity(todo) for todo in todos]


@router.get("/priority/{priority}", response_model=list[TodoResponseDTO])
async def get_todos_by_priority(
    priority: TodoPriority,
    service: TodoService = Depends(get_todo_service),
) -> list[TodoResponseDTO]:
    """Get todos by priority."""
    todos = service.get_todos_by_priority(priority)
    return [TodoResponseDTO.from_domain_entity(todo) for todo in todos]


@router.get("/stats/summary", response_model=TodoSummaryDTO)
async def get_todo_summary(
    service: TodoService = Depends(get_todo_service),
) -> TodoSummaryDTO:
    """Get todo statistics summary."""
    summary = service.get_user_todo_summary()
    return TodoSummaryDTO(**summary)


@router.get("/overdue", response_model=list[TodoResponseDTO])
async def get_overdue_todos(
    service: TodoService = Depends(get_todo_service),
) -> list[TodoResponseDTO]:
    """Get overdue todos."""
    todos = service.get_overdue_todos()
    return [TodoResponseDTO.from_domain_entity(todo) for todo in todos]


@router.get("/active", response_model=list[TodoResponseDTO])
async def get_active_todos(
    service: TodoService = Depends(get_todo_service),
) -> list[TodoResponseDTO]:
    """Get active todos (pending or in progress)."""
    todos = service.get_active_todos()
    return [TodoResponseDTO.from_domain_entity(todo) for todo in todos]


@router.post("/bulk/update-status", response_model=list[TodoResponseDTO])
async def bulk_update_status(
    bulk_data: BulkUpdateDTO,
    service: TodoService = Depends(get_todo_service),
) -> list[TodoResponseDTO]:
    """Update status for multiple todos."""
    todos = service.bulk_update_status(bulk_data.todo_ids, bulk_data.status)
    return [TodoResponseDTO.from_domain_entity(todo) for todo in todos]


@router.delete("/bulk/completed", status_code=http_status.HTTP_200_OK)
async def bulk_delete_completed(
    service: TodoService = Depends(get_todo_service),
) -> dict:
    """Delete all completed todos."""
    deleted_count = service.bulk_delete_completed_todos()
    return {"deleted_count": deleted_count}
