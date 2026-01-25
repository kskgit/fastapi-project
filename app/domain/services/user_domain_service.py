"""User Domain Service - Business logic for User entity operations."""

from app.domain.exceptions import (
    UniqueConstraintException,
    UserNotFoundException,
    ValidationException,
)
from app.domain.repositories import UserRepository


class UserDomainService:
    """Domain Service for User business logic.

    Handles complex business rules that involve multiple entities
    or require repository interactions while keeping the Entity pure.
    """

    async def validate_user_uniqueness(
        self, username: str, email: str, user_repository: UserRepository
    ) -> None:
        if await user_repository.find_by_username(username):
            raise UniqueConstraintException(
                f"Username '{username}' already exists",
                constraint_name="username_uniqueness",
            )

        if await user_repository.find_by_email(email):
            raise UniqueConstraintException(
                f"Email '{email}' already exists", constraint_name="email_uniqueness"
            )

    async def validate_user_exists(
        self, user_id: int, user_repository: UserRepository
    ) -> None:
        """Validate that user exists for todo operations (async version).

        Args:
            user_id: User ID to validate

        Raises:
            UserNotFoundException: If user does not exist
        """
        if not await user_repository.exists(user_id):
            raise UserNotFoundException(user_id)

    def validate_pagination_parameters(self, skip: int, limit: int) -> None:
        """Validate pagination parameters for user queries.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Raises:
            ValidationException: If pagination parameters are invalid

        Note:
            This is a domain rule: pagination must be within reasonable bounds
            to prevent system performance issues.
        """
        if limit > 1000:
            raise ValidationException("Limit cannot exceed 1000", field_name="limit")
        if skip < 0:
            raise ValidationException("Skip cannot be negative", field_name="skip")
