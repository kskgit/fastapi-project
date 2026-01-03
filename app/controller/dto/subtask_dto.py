from dataclasses import dataclass
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from app.domain.exceptions import ValidationException


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


class CreateSubTaskDTO(BaseModel):
    """DTO for creating a new subtask via API."""

    user_id: Annotated[
        int, Field(description="Todo owner user ID", frozen=True, strict=True)
    ]
    title: Annotated[
        str,
        Field(
            min_length=3,
            max_length=100,
            description="Todo title",
            frozen=True,
            strict=True,
        ),
    ]

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title - must not be None and at least 3 characters after strip."""
        return _normalize_title(v, empty_error="Title cannot be None or empty")

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: int) -> int:
        if v <= 0:
            raise ValidationException("User ID must be a positive integer")

        return v


@dataclass(slots=True, kw_only=True)
class SubtaskResult:
    """UseCase result placeholder until Subtask entity is introduced."""

    # TODO: サブタスクのドメインエンティティ実装後はこのプレースホルダを除去し、
    #  ドメインモデルから直接レスポンスDTOを生成する。
    id: int | None
    todo_id: int
    user_id: int
    title: str
    is_completed: bool
    completed_at: datetime | None
    created_at: datetime | None
    updated_at: datetime | None


class SubtaskResponseDTO(BaseModel):
    """Response DTO returned for Subtask operations."""

    id: int
    todo_id: int
    user_id: int
    title: str
    is_completed: bool
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_result(cls, result: SubtaskResult) -> "SubtaskResponseDTO":
        """Convert a SubtaskResult into an API response DTO."""
        if result.id is None:
            raise ValidationException("Cannot map subtask response without ID")
        if result.created_at is None:
            raise ValidationException("Cannot map subtask response without created_at")
        if result.updated_at is None:
            raise ValidationException("Cannot map subtask response without updated_at")

        return cls(
            id=result.id,
            todo_id=result.todo_id,
            user_id=result.user_id,
            title=result.title,
            is_completed=result.is_completed,
            completed_at=result.completed_at,
            created_at=result.created_at,
            updated_at=result.updated_at,
        )
