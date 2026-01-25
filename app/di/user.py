"""User-related dependency providers for the composition root."""

from fastapi import Depends

from app.di.common import (
    get_todo_repository,
    get_transaction_manager,
    get_user_repository,
)
from app.domain.repositories import TodoRepository, UserRepository
from app.domain.services import UserDomainService
from app.infrastructure.services import SQLAlchemyTransactionManager
from app.usecases.user import (
    CreateUserUseCase,
    DeleteUserUseCase,
    GetUserByIdUseCase,
    GetUsersUseCase,
    UpdateUserUseCase,
)


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
