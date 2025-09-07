"""Todo API routes.

This module contains all Todo-related API endpoints.
"""

from fastapi import APIRouter, Depends, Query
from fastapi import status as http_status

from app.api.dtos.todo_dto import (
    TodoCreateDTO,
    TodoResponseDTO,
    TodoUpdateDTO,
)
from app.composition.di import (
    get_create_todo_usecase,
    get_delete_todo_usecase,
    get_get_todo_by_id_usecase,
    get_get_todos_usecase,
    get_update_todo_usecase,
)
from app.domain.entities.todo import TodoPriority, TodoStatus
from app.usecases.todo.create_todo_usecase import CreateTodoUseCase
from app.usecases.todo.delete_todo_usecase import DeleteTodoUseCase
from app.usecases.todo.get_todo_by_id_usecase import GetTodoByIdUseCase
from app.usecases.todo.get_todos_usecase import GetTodosUseCase
from app.usecases.todo.update_todo_usecase import UpdateTodoUseCase

# Service layer has been removed in favor of UseCase pattern
# All service-based endpoints will be migrated to UseCase pattern


router = APIRouter(prefix="/todos", tags=["todos"])


@router.get("/", response_model=list[TodoResponseDTO])
async def get_todos(
    skip: int = Query(0, ge=0, description="Number of todos to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of todos to return"),
    status: TodoStatus | None = Query(None, description="Filter by status"),
    priority: TodoPriority | None = Query(None, description="Filter by priority"),
    usecase: GetTodosUseCase = Depends(get_get_todos_usecase),
) -> list[TodoResponseDTO]:
    """Get all todos with optional filtering."""
    # TODO: Replace with actual user_id from authentication
    user_id = 1
    todos = await usecase.execute(
        user_id=user_id, skip=skip, limit=limit, status=status, priority=priority
    )
    return [TodoResponseDTO.from_domain_entity(todo) for todo in todos]


@router.post(
    "/", response_model=TodoResponseDTO, status_code=http_status.HTTP_201_CREATED
)
async def create_todo(
    todo_data: TodoCreateDTO,
    usecase: CreateTodoUseCase = Depends(get_create_todo_usecase),
) -> TodoResponseDTO:
    """Create a new todo."""
    # TODO: Replace with actual user_id from authentication
    user_id = 1

    todo = await usecase.execute(
        title=todo_data.title,
        user_id=user_id,
        description=todo_data.description,
        due_date=todo_data.due_date,
        priority=todo_data.priority or TodoPriority.medium,
    )

    return TodoResponseDTO.from_domain_entity(todo)


@router.get("/{todo_id}", response_model=TodoResponseDTO)
async def get_todo(
    todo_id: int,
    usecase: GetTodoByIdUseCase = Depends(get_get_todo_by_id_usecase),
) -> TodoResponseDTO:
    """Get a specific todo by ID."""
    # TODO: Replace with actual user_id from authentication
    user_id = 1
    todo = await usecase.execute(todo_id=todo_id, user_id=user_id)
    return TodoResponseDTO.from_domain_entity(todo)


@router.put("/{todo_id}", response_model=TodoResponseDTO)
async def update_todo(
    todo_id: int,
    todo_data: TodoUpdateDTO,
    usecase: UpdateTodoUseCase = Depends(get_update_todo_usecase),
) -> TodoResponseDTO:
    """Update a specific todo."""
    # TODO: Replace with actual user_id from authentication
    user_id = 1
    todo = await usecase.execute(
        todo_id=todo_id,
        user_id=user_id,
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
    usecase: DeleteTodoUseCase = Depends(get_delete_todo_usecase),
) -> None:
    """Delete a specific todo."""
    # TODO: Replace with actual user_id from authentication
    user_id = 1
    deleted = await usecase.execute(todo_id=todo_id, user_id=user_id)
    if not deleted:
        from app.domain.exceptions import TodoNotFoundException

        raise TodoNotFoundException(todo_id)


@router.patch("/{todo_id}/complete", response_model=TodoResponseDTO)
async def complete_todo(
    todo_id: int,
    usecase: UpdateTodoUseCase = Depends(get_update_todo_usecase),
) -> TodoResponseDTO:
    """Mark a todo as completed."""
    # TODO: Replace with actual user_id from authentication
    user_id = 1
    todo = await usecase.execute(
        todo_id=todo_id, user_id=user_id, status=TodoStatus.completed
    )
    return TodoResponseDTO.from_domain_entity(todo)


@router.patch("/{todo_id}/start", response_model=TodoResponseDTO)
async def start_todo(
    todo_id: int,
    usecase: UpdateTodoUseCase = Depends(get_update_todo_usecase),
) -> TodoResponseDTO:
    """Mark a todo as in progress."""
    # TODO: Replace with actual user_id from authentication
    user_id = 1
    todo = await usecase.execute(
        todo_id=todo_id, user_id=user_id, status=TodoStatus.in_progress
    )
    return TodoResponseDTO.from_domain_entity(todo)


@router.patch("/{todo_id}/cancel", response_model=TodoResponseDTO)
async def cancel_todo(
    todo_id: int,
    usecase: UpdateTodoUseCase = Depends(get_update_todo_usecase),
) -> TodoResponseDTO:
    """Cancel a todo."""
    # TODO: Replace with actual user_id from authentication
    user_id = 1
    todo = await usecase.execute(
        todo_id=todo_id, user_id=user_id, status=TodoStatus.canceled
    )
    return TodoResponseDTO.from_domain_entity(todo)


@router.get("/status/{status}", response_model=list[TodoResponseDTO])
async def get_todos_by_status(
    status: TodoStatus,
    usecase: GetTodosUseCase = Depends(get_get_todos_usecase),
) -> list[TodoResponseDTO]:
    """Get todos by status."""
    # TODO: Replace with actual user_id from authentication
    user_id = 1
    todos = await usecase.execute(user_id=user_id, status=status)
    return [TodoResponseDTO.from_domain_entity(todo) for todo in todos]


@router.get("/priority/{priority}", response_model=list[TodoResponseDTO])
async def get_todos_by_priority(
    priority: TodoPriority,
    usecase: GetTodosUseCase = Depends(get_get_todos_usecase),
) -> list[TodoResponseDTO]:
    """Get todos by priority."""
    # TODO: Replace with actual user_id from authentication
    user_id = 1
    todos = await usecase.execute(user_id=user_id, priority=priority)
    return [TodoResponseDTO.from_domain_entity(todo) for todo in todos]
