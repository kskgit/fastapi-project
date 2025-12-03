"""Create User UseCase implementation."""

from app.core.transaction_manager import TransactionManager
from app.domain.entities.user import User, UserRole
from app.domain.repositories.user_repository import UserRepository
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
        self,
        username: str,
        email: str,
        role: UserRole,
        full_name: str | None = None,
    ) -> User:
        """Execute the create user use case.

        Args:
            username: User's username (required, unique)
            email: User's email address (required, unique)
            role: User's role (viewer/member/admin)
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
            await self.user_domain_service.validate_user_uniqueness(
                username=username,
                email=email,
                user_repository=self.user_repository,
            )

            user = User.create(
                username=username,
                email=email,
                full_name=full_name,
                role=role,
            )

            return await self.user_repository.create(user)
