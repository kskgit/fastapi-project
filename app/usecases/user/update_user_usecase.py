"""Update User UseCase implementation."""

from app.core.transaction_manager import TransactionManager
from app.domain.entities.user import User, UserRole
from app.domain.exceptions import UserNotFoundException
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

    def __init__(
        self, transaction_manager: TransactionManager, user_repository: UserRepository
    ):
        """Initialize with transaction manager and repository dependencies.

        Args:
            transaction_manager: Transaction manager for database operations
            user_repository: UserRepository interface implementation
        """
        self.transaction_manager = transaction_manager
        self.user_repository = user_repository
        self.user_domain_service = UserDomainService()

    async def execute(
        self,
        user_id: int,
        username: str | None = None,
        email: str | None = None,
        full_name: str | None = None,
        role: UserRole | None = None,
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
            Domain exceptions are handled by FastAPI exception handlers in main.py.
            Transaction management is handled explicitly within this method.
        """
        async with self.transaction_manager.begin_transaction():
            user = await self._get_user(user_id)
            await self.user_domain_service.validate_user_update_uniqueness(
                user_id, user, username, email, self.user_repository
            )

            user.update(
                username=username,
                email=email,
                full_name=full_name,
                role=role,
            )
            return await self.user_repository.update(user)

    async def _get_user(self, user_id: int) -> User:
        """Validate that the user exists."""
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        return user
