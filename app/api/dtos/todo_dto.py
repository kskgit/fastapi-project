from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.domain.entities.todo import Todo as TodoEntity
from app.domain.entities.todo import TodoPriority, TodoStatus


class TodoCreateDTO(BaseModel):
    """DTO for creating a new todo via API."""

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
        if not v:
            raise ValueError("Title cannot be None or empty")

        stripped = v.strip()
        if len(stripped) < 3:
            raise ValueError(
                "Title must be at least 3 characters long after removing whitespace"
            )

        return stripped


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

        if not v:
            raise ValueError("Title cannot be empty")

        stripped = v.strip()
        if len(stripped) < 3:
            raise ValueError(
                "Title must be at least 3 characters long after removing whitespace"
            )

        return stripped


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
    def from_domain_entity(cls, entity: TodoEntity) -> "TodoResponseDTO":
        """Convert domain entity to response DTO."""
        if entity.id is None:
            raise ValueError("Cannot create response DTO from entity without ID")
        if entity.created_at is None:
            raise ValueError("Cannot create response DTO without created_at")
        if entity.updated_at is None:
            raise ValueError("Cannot create response DTO without updated_at")

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
