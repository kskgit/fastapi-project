from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TodoPriority(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class TodoStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    canceled = "canceled"


class TodoBase(BaseModel):
    title: str = Field(..., description="Title")
    description: str | None = Field(None, description="Description")
    due_date: datetime | None = Field(None, description="Due date")
    priority: TodoPriority = Field(TodoPriority.medium, description="Priority")
    status: TodoStatus = Field(TodoStatus.pending, description="Status")


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    priority: TodoPriority | None = None
    status: TodoStatus | None = None


class Todo(TodoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
