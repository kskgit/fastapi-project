from abc import ABC, abstractmethod

from app.clean.domain.entities.user import User


class UserRepository(ABC):
    """Abstract Repository Interface for User operations.

    Service layer depends only on this interface, not on implementation details.
    This ensures complete separation from database concerns.
    """

    @abstractmethod
    def save(self, user: User) -> User:
        """Save a user (create or update).

        Args:
            user: User domain entity to save

        Returns:
            Saved user with updated fields (id, timestamps)
        """
        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> User | None:
        """Find user by ID.

        Args:
            user_id: ID of the user to find

        Returns:
            User domain entity if found, None otherwise
        """
        pass

    @abstractmethod
    def find_by_username(self, username: str) -> User | None:
        """Find user by username.

        Args:
            username: Username to search for

        Returns:
            User domain entity if found, None otherwise
        """
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> User | None:
        """Find user by email address.

        Args:
            email: Email address to search for

        Returns:
            User domain entity if found, None otherwise
        """
        pass

    @abstractmethod
    def find_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Find all users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of user domain entities
        """
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """Delete user by ID.

        Args:
            user_id: ID of the user to delete

        Returns:
            True if deleted successfully, False if not found
        """
        pass

    @abstractmethod
    def exists(self, user_id: int) -> bool:
        """Check if user exists.

        Args:
            user_id: ID of the user to check

        Returns:
            True if user exists, False otherwise
        """
        pass

    @abstractmethod
    def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username.

        Args:
            username: Username to check

        Returns:
            True if user exists, False otherwise
        """
        pass

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email.

        Args:
            email: Email to check

        Returns:
            True if user exists, False otherwise
        """
        pass

    @abstractmethod
    def count_total(self) -> int:
        """Count total users.

        Returns:
            Total number of users
        """
        pass
