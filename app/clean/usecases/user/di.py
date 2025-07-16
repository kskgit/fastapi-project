"""User endpoints dependency injection.

This module contains factory functions for User-related UseCases.
These functions will be used by FastAPI's dependency injection system.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.clean.core.database_clean import get_db
from app.clean.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from app.clean.usecases.user.create_user_usecase import CreateUserUseCase
from app.clean.usecases.user.delete_user_usecase import DeleteUserUseCase
from app.clean.usecases.user.get_user_by_id_usecase import GetUserByIdUseCase
from app.clean.usecases.user.get_users_usecase import GetUsersUseCase
from app.clean.usecases.user.update_user_usecase import UpdateUserUseCase


def get_create_user_usecase(db: Session = Depends(get_db)) -> CreateUserUseCase:
    """Factory function for CreateUserUseCase.

    Creates UseCase instance with required repository dependencies.

    Args:
        db: Database session dependency

    Returns:
        CreateUserUseCase: UseCase instance with injected dependencies
    """
    user_repository = SQLAlchemyUserRepository(db)
    return CreateUserUseCase(user_repository)


def get_get_users_usecase(db: Session = Depends(get_db)) -> GetUsersUseCase:
    """Factory function for GetUsersUseCase.

    Creates UseCase instance with required repository dependencies.

    Args:
        db: Database session dependency

    Returns:
        GetUsersUseCase: UseCase instance with injected dependencies
    """
    user_repository = SQLAlchemyUserRepository(db)
    return GetUsersUseCase(user_repository)


def get_get_user_by_id_usecase(db: Session = Depends(get_db)) -> GetUserByIdUseCase:
    """Factory function for GetUserByIdUseCase.

    Creates UseCase instance with required repository dependencies.

    Args:
        db: Database session dependency

    Returns:
        GetUserByIdUseCase: UseCase instance with injected dependencies
    """
    user_repository = SQLAlchemyUserRepository(db)
    return GetUserByIdUseCase(user_repository)


def get_update_user_usecase(db: Session = Depends(get_db)) -> UpdateUserUseCase:
    """Factory function for UpdateUserUseCase.

    Creates UseCase instance with required repository dependencies.

    Args:
        db: Database session dependency

    Returns:
        UpdateUserUseCase: UseCase instance with injected dependencies
    """
    user_repository = SQLAlchemyUserRepository(db)
    return UpdateUserUseCase(user_repository)


def get_delete_user_usecase(db: Session = Depends(get_db)) -> DeleteUserUseCase:
    """Factory function for DeleteUserUseCase.

    Creates UseCase instance with required repository dependencies.

    Args:
        db: Database session dependency

    Returns:
        DeleteUserUseCase: UseCase instance with injected dependencies
    """
    user_repository = SQLAlchemyUserRepository(db)
    return DeleteUserUseCase(user_repository)
