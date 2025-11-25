"""User-related dependency providers for the composition root."""

from fastapi import Depends

from app.di.common import (
    get_todo_repository,
    get_transaction_manager,
    get_user_repository,
)
from app.domain.repositories.todo_repository import TodoRepository
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.user_domain_service import UserDomainService
from app.infrastructure.services.sqlalchemy_transaction_manager import (
    SQLAlchemyTransactionManager,
)
from app.usecases.user.create_user_usecase import CreateUserUseCase
from app.usecases.user.delete_user_usecase import DeleteUserUseCase
from app.usecases.user.get_user_by_id_usecase import GetUserByIdUseCase
from app.usecases.user.get_users_usecase import GetUsersUseCase
from app.usecases.user.update_user_usecase import UpdateUserUseCase


def get_user_domain_service() -> UserDomainService:
    """Factory function for UserDomainService."""
    return UserDomainService()


def get_create_user_usecase(
    transaction_manager: SQLAlchemyTransactionManager = Depends(
        get_transaction_manager
    ),
    user_repository: UserRepository = Depends(get_user_repository),
) -> CreateUserUseCase:
    """Factory function for CreateUserUseCase."""
    return CreateUserUseCase(transaction_manager, user_repository)


def get_get_users_usecase(
    user_repository: UserRepository = Depends(get_user_repository),
) -> GetUsersUseCase:
    """Factory function for GetUsersUseCase."""
    return GetUsersUseCase(user_repository)


def get_get_user_by_id_usecase(
    user_repository: UserRepository = Depends(get_user_repository),
) -> GetUserByIdUseCase:
    """Factory function for GetUserByIdUseCase."""
    return GetUserByIdUseCase(user_repository)


def get_update_user_usecase(
    transaction_manager: SQLAlchemyTransactionManager = Depends(
        get_transaction_manager
    ),
    user_repository: UserRepository = Depends(get_user_repository),
) -> UpdateUserUseCase:
    """Factory function for UpdateUserUseCase."""
    return UpdateUserUseCase(transaction_manager, user_repository)


def get_delete_user_usecase(
    transaction_manager: SQLAlchemyTransactionManager = Depends(
        get_transaction_manager
    ),
    user_repository: UserRepository = Depends(get_user_repository),
    todo_repository: TodoRepository = Depends(get_todo_repository),
) -> DeleteUserUseCase:
    """Factory function for DeleteUserUseCase."""
    return DeleteUserUseCase(transaction_manager, user_repository, todo_repository)
