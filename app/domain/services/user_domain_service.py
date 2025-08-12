"""User Domain Service - Business logic for User entity operations."""

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository

from ..exceptions import UniqueConstraintException


class UserDomainService:
    """Domain Service for User business logic.

    Handles complex business rules that involve multiple entities
    or require repository interactions while keeping the Entity pure.
    """

    async def validate_user_creation_uniqueness(
        self, username: str, email: str, user_repository: UserRepository
    ) -> None:
        """Validate uniqueness constraints for user creation.

        Args:
            username: Username to validate
            email: Email to validate
            user_repository: Repository for user data access

        Raises:
            ValueError: If username or email already exists

        Note:
            This is a domain rule: usernames and emails must be unique
            across the system.
        """
        if await user_repository.find_by_username(username):
            raise UniqueConstraintException(
                f"Username '{username}' already exists",
                constraint_name="username_uniqueness",
            )

        if await user_repository.find_by_email(email):
            raise UniqueConstraintException(
                f"Email '{email}' already exists", constraint_name="email_uniqueness"
            )

    async def validate_user_update_uniqueness(
        self,
        user_id: int,
        current_user: User,
        new_username: str | None,
        new_email: str | None,
        user_repository: UserRepository,
    ) -> None:
        """Validate uniqueness constraints for user update.

        Args:
            user_id: ID of the user being updated
            current_user: Current user entity
            new_username: New username (None if not updating)
            new_email: New email (None if not updating)
            user_repository: Repository for user data access

        Raises:
            ValueError: If username or email already exists

        Note:
            This is a domain rule: usernames and emails must be unique
            across the system.
        """
        if new_username is not None and new_username != current_user.username:
            await self._validate_username_uniqueness(
                user_id, new_username, user_repository
            )

        if new_email is not None and new_email != current_user.email:
            await self._validate_email_uniqueness(user_id, new_email, user_repository)

    async def _validate_username_uniqueness(
        self, user_id: int, username: str, user_repository: UserRepository
    ) -> None:
        """Validate that username is unique in the system."""
        existing_user = await user_repository.find_by_username(username)
        if existing_user and existing_user.id != user_id:
            raise UniqueConstraintException(
                f"Username '{username}' already exists",
                constraint_name="username_uniqueness",
            )

    async def _validate_email_uniqueness(
        self, user_id: int, email: str, user_repository: UserRepository
    ) -> None:
        """Validate that email is unique in the system."""
        existing_user = await user_repository.find_by_email(email)
        if existing_user and existing_user.id != user_id:
            raise UniqueConstraintException(
                f"Email '{email}' already exists", constraint_name="email_uniqueness"
            )
