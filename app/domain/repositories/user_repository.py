from abc import ABC, abstractmethod

from app.domain.entities.user import User


class UserRepository(ABC):
    """Abstract Repository Interface for User operations.

    Service layer depends only on this interface, not on implementation details.
    This ensures complete separation from database concerns with async support.
    """

    @abstractmethod
    async def create(self, user: User) -> User:
        """Persist a new user entity."""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user entity."""
        pass

    @abstractmethod
    async def find_by_id(self, user_id: int) -> User | None:
        """Find user by ID.

        Args:
            user_id: ID of the user to find

        Returns:
            User domain entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_by_username(self, username: str) -> User | None:
        """Find user by username.

        Args:
            username: Username to search for

        Returns:
            User domain entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None:
        """Find user by email.

        Args:
            email: Email to search for

        Returns:
            User domain entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_all(self) -> list[User]:
        """Find all users.

        Returns:
            List of all user domain entities
        """
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Delete user by ID.

        Args:
            user_id: ID of the user to delete

        Returns:
            True if deleted successfully, False if not found
        """
        pass

    @abstractmethod
    async def exists(self, user_id: int) -> bool:
        """Check if user exists.

        Args:
            user_id: ID of the user to check

        Returns:
            True if user exists, False otherwise
        """
        pass

    @abstractmethod
    async def count_total(self) -> int:
        """Count total users.

        Returns:
            Total number of users
        """
        pass
