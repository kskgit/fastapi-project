from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, field_validator

from app.domain.entities import Todo as TodoEntity
from app.domain.entities import TodoPriority, TodoStatus
from app.domain.exceptions import ValidationException

if TYPE_CHECKING:
    from app.controller.dto.subtask_dto import SubtaskResponseDTO
    from app.usecases.todo import TodoWithSubtasks


def _normalize_title(value: str, *, empty_error: str) -> str:
    """Common title normalization shared across create/update DTOs."""
    if not value:
        raise ValidationException(empty_error)

    stripped = value.strip()
    if len(stripped) < 3:
        raise ValidationException(
            "Title must be at least 3 characters long after removing whitespace"
        )

    return stripped


class CreateTodoDTO(BaseModel):
    """DTO for creating a new todo via API."""

    user_id: int = Field(..., description="Todo owner user ID")
    title: str = Field(..., min_length=3, max_length=100, description="Todo title")
    description: str | None = Field(
        None, max_length=500, description="Todo description"
    )
    due_date: datetime | None = Field(None, description="Due date")
    priority: TodoPriority = Field(TodoPriority.medium, description="Todo priority")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title - must not be None and at least 3 characters after strip."""
        return _normalize_title(v, empty_error="Title cannot be None or empty")

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: int) -> int:
        """Validate user_id is a positive integer."""
        if v is None:
            raise ValidationException("User ID is required")

        if v <= 0:
            raise ValidationException("User ID must be a positive integer")

        return v


class TodoUpdateDTO(BaseModel):
    """DTO for updating an existing todo via API."""

    title: str | None = Field(
        None, min_length=3, max_length=100, description="Todo title"
    )
    description: str | None = Field(
        None, max_length=500, description="Todo description"
    )
    due_date: datetime | None = Field(None, description="Due date")
    priority: TodoPriority | None = Field(None, description="Todo priority")
    status: TodoStatus | None = Field(None, description="Todo status")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        """Validate title if provided - must be at least 3 characters after strip."""
        if v is None:
            return None
        return _normalize_title(v, empty_error="Title cannot be empty")


class TodoResponseDTO(BaseModel):
    """DTO for todo responses from API."""

    id: int
    title: str
    description: str | None
    due_date: datetime | None
    status: TodoStatus
    priority: TodoPriority
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain_entity(cls, entity: TodoEntity) -> TodoResponseDTO:
        """Convert domain entity to response DTO."""
        if entity.id is None:
            raise ValidationException(
                "Cannot create response DTO from entity without ID"
            )
        if entity.created_at is None:
            raise ValidationException("Cannot create response DTO without created_at")
        if entity.updated_at is None:
            raise ValidationException("Cannot create response DTO without updated_at")

        return cls(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            due_date=entity.due_date,
            status=entity.status,
            priority=entity.priority,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class TodoWithSubtasksResponseDTO(BaseModel):
    """DTO for todo response with subtasks from API."""

    id: int
    title: str
    description: str | None
    due_date: datetime | None
    status: TodoStatus
    priority: TodoPriority
    created_at: datetime
    updated_at: datetime
    subtasks: list[SubtaskResponseDTO]

    @classmethod
    def from_usecase_result(
        cls, result: TodoWithSubtasks
    ) -> TodoWithSubtasksResponseDTO:
        """Convert usecase result to response DTO."""
        from app.controller.dto.subtask_dto import SubtaskResponseDTO

        todo = result.todo
        if todo.id is None:
            raise ValidationException(
                "Cannot create response DTO from entity without ID"
            )
        if todo.created_at is None:
            raise ValidationException("Cannot create response DTO without created_at")
        if todo.updated_at is None:
            raise ValidationException("Cannot create response DTO without updated_at")

        return cls(
            id=todo.id,
            title=todo.title,
            description=todo.description,
            due_date=todo.due_date,
            status=todo.status,
            priority=todo.priority,
            created_at=todo.created_at,
            updated_at=todo.updated_at,
            subtasks=[
                SubtaskResponseDTO.from_domain_entity(s) for s in result.subtasks
            ],
        )


class TodoSummaryDTO(BaseModel):
    """DTO for todo summary statistics."""

    total: int
    pending: int
    in_progress: int
    completed: int
    canceled: int
    overdue: int
    active: int


class BulkUpdateDTO(BaseModel):
    """DTO for bulk operations."""

    todo_ids: list[int] = Field(..., description="List of todo IDs")
    status: TodoStatus = Field(..., description="New status to apply")
