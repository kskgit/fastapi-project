from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """Domain Entity for User - Pure business logic, no database dependencies.

    This entity represents a user in the system who can own and manage todos.
    """

    username: str
    email: str
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def create(
        cls,
        username: str,
        email: str,
    ) -> "User":
        """Create a new User.

        Args:
            username: Unique username for the user
            email: User's email address

        Returns:
            User: New user entity with pending status

        Note:
            Username and email validation is handled by API DTOs.
        """
        return cls(
            username=username,
            email=email,
        )

    def update_username(self, username: str) -> None:
        """Update username.

        Args:
            username: New username

        Note:
            Username validation is handled by API DTOs.
        """
        self.username = username

    def update_email(self, email: str) -> None:
        """Update email address.

        Args:
            email: New email address

        Note:
            Email validation is handled by API DTOs.
        """
        self.email = email

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
