"""Update User UseCase implementation."""

from app.domain.entities.user import User
from app.domain.exceptions import UserNotFoundException, ValidationException
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.user_domain_service import UserDomainService


class UpdateUserUseCase:
    """UseCase for updating an existing User.

    Single Responsibility: Handle the update of a user with proper
    business logic validation and error handling.

    Dependencies:
    - Only depends on Domain layer (UserRepository interface)
    - No dependencies on API, Services, or Infrastructure layers
    """

    def __init__(self, user_repository: UserRepository):
        """Initialize with repository dependencies.

        Args:
            user_repository: UserRepository interface implementation
        """
        self.user_repository = user_repository
        self.user_domain_service = UserDomainService()

    async def execute(
        self,
        user_id: int,
        username: str | None = None,
        email: str | None = None,
        full_name: str | None = None,
    ) -> User:
        """Execute the update user use case.

        Args:
            user_id: ID of the user to update
            username: Optional new username
            email: Optional new email
            full_name: Optional new full name

        Returns:
            User: Updated user entity

        Raises:
            UserNotFoundException: If user not found
            ValueError: If validation fails (duplicate username/email,
                no fields to update)

        Note:
            At least one field must be provided for update.
            Exceptions are handled by FastAPI exception handlers in main.py.
        """
        user = await self._validate_user_exists(user_id)
        self._validate_update_fields(username, email, full_name)
        await self.user_domain_service.validate_user_update_uniqueness(
            user_id, user, username, email, self.user_repository
        )
        self._update_user_fields(user, username, email, full_name)
        return await self.user_repository.save(user)

    async def _validate_user_exists(self, user_id: int) -> User:
        """Validate that the user exists."""
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        return user

    def _validate_update_fields(
        self, username: str | None, email: str | None, full_name: str | None
    ) -> None:
        """Validate that at least one field is provided for update."""
        if all(param is None for param in [username, email, full_name]):
            raise ValidationException("At least one field must be provided for update")

    def _update_user_fields(
        self, user: User, username: str | None, email: str | None, full_name: str | None
    ) -> None:
        """Update user fields if provided."""
        if username is not None:
            user.username = username
        if email is not None:
            user.email = email
        if full_name is not None:
            user.full_name = full_name
