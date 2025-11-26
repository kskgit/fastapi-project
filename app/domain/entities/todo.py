from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from ..exceptions import (
    StateTransitionException,
    TodoNotFoundException,
    ValidationException,
)

if TYPE_CHECKING:
    from app.domain.repositories.user_repository import UserRepository
    from app.domain.services.todo_domain_service import TodoDomainService


class TodoPriority(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class TodoStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    canceled = "canceled"


@dataclass
class Todo:
    """Domain Entity for Todo - Pure business logic, no database dependencies.

    Note: Basic field validation (length, format) is handled by API DTOs.
    This entity focuses on business logic and state management.
    """

    title: str
    user_id: int
    description: str | None = None
    due_date: datetime | None = None
    status: TodoStatus = TodoStatus.pending
    priority: TodoPriority = TodoPriority.medium
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def create(
        cls,
        title: str,
        user_id: int,
        description: str | None = None,
        due_date: datetime | None = None,
        priority: TodoPriority = TodoPriority.medium,
    ) -> Todo:
        """Create a new Todo.

        Args:
            title: Todo title
            user_id: ID of the user who owns this todo
            description: Optional todo description
            due_date: Optional due date
            priority: Todo priority (defaults to medium)

        Returns:
            Todo: New todo entity with pending status

        Note:
            Basic validation (title length, description length) is handled by DTOs.
            This method focuses on domain-specific business logic only.
        """
        return cls(
            title=title,  # DTOで既にtrimされている
            user_id=user_id,
            description=description,
            due_date=due_date,
            priority=priority,
            status=TodoStatus.pending,
        )

    def mark_completed(self) -> None:
        """Mark todo as completed with business validation."""
        if self.status == TodoStatus.completed:
            raise StateTransitionException(
                "Todo is already completed",
                current_state="completed",
                attempted_state="completed",
            )

        if self.status == TodoStatus.canceled:
            raise StateTransitionException(
                "Cannot complete a canceled todo",
                current_state="canceled",
                attempted_state="completed",
            )

        self.status = TodoStatus.completed

    def mark_in_progress(self) -> None:
        """Mark todo as in progress."""
        if self.status == TodoStatus.completed:
            raise StateTransitionException(
                "Cannot change completed todo to in progress",
                current_state="completed",
                attempted_state="in_progress",
            )

        if self.status == TodoStatus.canceled:
            raise StateTransitionException(
                "Cannot change canceled todo to in progress",
                current_state="canceled",
                attempted_state="in_progress",
            )

        self.status = TodoStatus.in_progress

    def cancel(self) -> None:
        """Cancel the todo."""
        if self.status == TodoStatus.completed:
            raise StateTransitionException(
                "Cannot cancel a completed todo",
                current_state="completed",
                attempted_state="canceled",
            )

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

    def is_owned_by(self, user_id: int) -> bool:
        """Check if this todo is owned by the specified user.

        Args:
            user_id: User ID to check ownership against

        Returns:
            bool: True if the todo is owned by the user, False otherwise
        """
        return self.user_id == user_id

    def update(
        self,
        user_id: int,
        user_repository: UserRepository,
        todo_domain_service: TodoDomainService,
        title: str | None,
        description: str | None,
        due_date: datetime | None,
        status: TodoStatus | None,
        priority: TodoPriority | None,
    ) -> None:
        if self.user_id != user_id:
            """
            想定ユースケースであれば、idはこのタイミングでは必ず存在するが
            型チェック解消のためis Noneケースを用意

            攻撃者にTodoが存在することが伝わらないようにするため、あえてTodoNotFoundExceptionとする
            """
            raise TodoNotFoundException(self.id if self.id is not None else -1)

        self._validate_atleast_one_field_provided(
            title, description, due_date, status, priority
        )

        self._update_fields(title, description, due_date, status, priority)

    def _validate_atleast_one_field_provided(self, *fields: object) -> None:
        """Validate that at least one field is provided for update.

        Args:
            *fields: Variable number of field values to check

        Raises:
            ValueError: If no fields are provided for update

        Note:
            This is a domain rule: Update operations must modify at least one field.
        """
        if all(field is None for field in fields):
            raise ValidationException("At least one field must be provided for update")

    def _update_fields(
        self,
        title: str | None,
        description: str | None,
        due_date: datetime | None,
        status: TodoStatus | None,
        priority: TodoPriority | None,
    ) -> None:
        if title is not None:
            self.update_title(title)
        if description is not None:
            self.update_description(description)
        if due_date is not None:
            self.update_due_date(due_date)
        if status is not None:
            self.status = status
        if priority is not None:
            self.update_priority(priority)

    class Config:
        use_enum_values = True
