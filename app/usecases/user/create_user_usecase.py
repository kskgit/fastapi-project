"""Create User UseCase implementation."""

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.transaction_manager import TransactionManager
from app.domain.services.user_domain_service import UserDomainService


class CreateUserUseCase:
    """UseCase for creating a new User.

    Single Responsibility: Handle the creation of a new User with proper
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
        self, username: str, email: str, full_name: str | None = None
    ) -> User:
        """Execute the create user use case.

        Args:
            username: User's username (required, unique)
            email: User's email address (required, unique)
            full_name: User's full name (optional)

        Returns:
            User: Created user entity

        Raises:
            ValueError: If username or email already exists

        Note:
            Transaction management is handled explicitly within this method.
        """
        async with (
            self.transaction_manager.begin_transaction()
        ):  # Explicit transaction boundary
            # Validate uniqueness constraints
            await self.user_domain_service.validate_user_creation_uniqueness(
                username, email, self.user_repository
            )

            # Create new user
            user = User.create(username=username, email=email, full_name=full_name)

            return await self.user_repository.save(user)
        # Transaction automatically commits on success or rolls back on exception
