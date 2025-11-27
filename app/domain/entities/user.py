from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.domain.exceptions import ValidationException


class UserRole(StrEnum):
    """User role definitions."""

    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


@dataclass
class User:
    """Domain Entity for User - Pure business logic, no database dependencies.

    This entity represents a user in the system who can own and manage todos.
    """

    username: str
    email: str
    full_name: str | None = None
    role: UserRole = UserRole.MEMBER
    is_active: bool = True
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def create(
        cls,
        username: str,
        email: str,
        full_name: str | None = None,
        role: UserRole = UserRole.MEMBER,
    ) -> "User":
        """Create a new User.

        Args:
            username: Unique username for the user
            email: User's email address
            role: User role (viewer/member/admin)

        Returns:
            User: New user entity with pending status

        Note:
            Username and email validation is handled by API DTOs.
        """
        return cls(
            username=username,
            email=email,
            full_name=full_name,
            role=role,
        )

    def update_username(self, username: str) -> None:
        """Update username.

        Args:
            username: New username

        Note:
            Username validation is handled by API DTOs.
        """
        self.username = username

    # todo emailの独自型利用へ変更する
    def update_email(self, email: str) -> None:
        """Update email address.

        Args:
            email: New email address

        Note:
            Email validation is handled by API DTOs.
        """
        self.email = email

    def update_full_name(self, full_name: str | None) -> None:
        """Update full name."""
        self.full_name = full_name

    def update_role(self, role: UserRole) -> None:
        """Update full name."""
        self.role = role

    def can_manage_todo(self, todo_user_id: int) -> bool:
        """Check if this user can manage the specified todo.

        Args:
            todo_user_id: User ID associated with the todo

        Returns:
            bool: True if user can manage the todo, False otherwise
        """
        if self.id is None:
            return False
        return self.id == todo_user_id

    def _validate_atleast_one_field_provided(
        self, username: str | None, email: str | None, full_name: str | None
    ) -> None:
        """Ensure at least one field is provided for update."""
        if all(field is None for field in (username, email, full_name)):
            raise ValidationException("At least one field must be provided for update")

    def update(
        self,
        username: str | None,
        email: str | None,
        full_name: str | None,
        role: UserRole | None,
    ) -> None:
        self._validate_atleast_one_field_provided(username, email, full_name)
        """Apply provided field changes."""
        if username is not None:
            self.update_username(username)
        if email is not None:
            self.update_email(email)
        if full_name is not None:
            self.update_full_name(full_name)
        if role is not None:
            self.update_role(role)
