from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class TodoPriority(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class TodoStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    canceled = "canceled"


class Todo(BaseModel):
    """Domain Entity for Todo - Pure business logic, no database dependencies.

    Note: Basic field validation (length, format) is handled by API DTOs.
    This entity focuses on business logic and state management.
    """

    id: int | None = None
    title: str
    description: str | None = None
    due_date: datetime | None = None
    status: TodoStatus = TodoStatus.pending
    priority: TodoPriority = TodoPriority.medium
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def create(
        cls,
        title: str,
        description: str | None = None,
        due_date: datetime | None = None,
        priority: TodoPriority = TodoPriority.medium,
    ) -> "Todo":
        """Create a new Todo.

        Note: Basic validation (title length, description length) is handled by DTOs.
        This method focuses on domain-specific business logic only.
        """
        return cls(
            title=title,  # DTOで既にtrimされている
            description=description,
            due_date=due_date,
            priority=priority,
            status=TodoStatus.pending,
        )

    def mark_completed(self) -> None:
        """Mark todo as completed with business validation."""
        if self.status == TodoStatus.completed:
            raise ValueError("Todo is already completed")

        if self.status == TodoStatus.canceled:
            raise ValueError("Cannot complete a canceled todo")

        self.status = TodoStatus.completed

    def mark_in_progress(self) -> None:
        """Mark todo as in progress."""
        if self.status == TodoStatus.completed:
            raise ValueError("Cannot change completed todo to in progress")

        if self.status == TodoStatus.canceled:
            raise ValueError("Cannot change canceled todo to in progress")

        self.status = TodoStatus.in_progress

    def cancel(self) -> None:
        """Cancel the todo."""
        if self.status == TodoStatus.completed:
            raise ValueError("Cannot cancel a completed todo")

        self.status = TodoStatus.canceled

    def is_overdue(self) -> bool:
        """Check if todo is overdue."""
        if not self.due_date:
            return False

        return self.due_date < datetime.now() and self.status in [
            TodoStatus.pending,
            TodoStatus.in_progress,
        ]

    def can_be_deleted(self) -> bool:
        """Check if todo can be deleted."""
        return self.status != TodoStatus.in_progress

    def update_title(self, title: str) -> None:
        """Update title.

        Note: Title validation is handled by API DTOs.
        """
        self.title = title

    def update_description(self, description: str | None) -> None:
        """Update description.

        Note: Description validation is handled by API DTOs.
        """
        self.description = description

    def update_priority(self, priority: TodoPriority) -> None:
        """Update priority."""
        self.priority = priority

    def update_due_date(self, due_date: datetime | None) -> None:
        """Update due date."""
        self.due_date = due_date

    def can_change_status_to(self, new_status: TodoStatus) -> bool:
        """Check if status can be changed to new_status."""
        if self.status == new_status:
            return False

        if self.status == TodoStatus.completed and new_status == TodoStatus.pending:
            return False

        if self.status == TodoStatus.canceled and new_status in [
            TodoStatus.pending,
            TodoStatus.in_progress,
        ]:
            return False

        return True

    class Config:
        use_enum_values = True
