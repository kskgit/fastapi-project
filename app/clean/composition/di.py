"""Dependency Injection configuration for the entire application.

This is the Composition Root - the only layer allowed to depend on all other layers.
It assembles concrete implementations and provides factory functions for FastAPI DI.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.clean.core.database_clean import get_db
from app.clean.domain.repositories.todo_repository import TodoRepository
from app.clean.domain.repositories.user_repository import UserRepository
from app.clean.infrastructure.repositories.sqlalchemy_todo_repository import (
    SQLAlchemyTodoRepository,
)
from app.clean.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from app.clean.usecases.todo.create_todo_usecase import CreateTodoUseCase
from app.clean.usecases.todo.delete_todo_usecase import DeleteTodoUseCase
from app.clean.usecases.todo.get_todo_by_id_usecase import GetTodoByIdUseCase
from app.clean.usecases.todo.get_todos_usecase import GetTodosUseCase
from app.clean.usecases.todo.update_todo_usecase import UpdateTodoUseCase
from app.clean.usecases.user.create_user_usecase import CreateUserUseCase
from app.clean.usecases.user.delete_user_usecase import DeleteUserUseCase
from app.clean.usecases.user.get_user_by_id_usecase import GetUserByIdUseCase
from app.clean.usecases.user.get_users_usecase import GetUsersUseCase
from app.clean.usecases.user.update_user_usecase import UpdateUserUseCase

# =============================================================================
# Repository Factory Functions
# =============================================================================


def get_todo_repository(db: Session = Depends(get_db)) -> TodoRepository:
    """Factory function for TodoRepository.

    Args:
        db: Database session dependency

    Returns:
        TodoRepository: Concrete repository implementation
    """
    return SQLAlchemyTodoRepository(db)


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """Factory function for UserRepository.

    Args:
        db: Database session dependency

    Returns:
        UserRepository: Concrete repository implementation
    """
    return SQLAlchemyUserRepository(db)


# =============================================================================
# Todo UseCase Factory Functions
# =============================================================================


def get_create_todo_usecase(
    todo_repository: TodoRepository = Depends(get_todo_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> CreateTodoUseCase:
    """Factory function for CreateTodoUseCase.

    Args:
        todo_repository: Todo repository dependency
        user_repository: User repository dependency

    Returns:
        CreateTodoUseCase: UseCase instance with injected dependencies
    """
    return CreateTodoUseCase(todo_repository, user_repository)


def get_get_todos_usecase(
    todo_repository: TodoRepository = Depends(get_todo_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> GetTodosUseCase:
    """Factory function for GetTodosUseCase.

    Args:
        todo_repository: Todo repository dependency
        user_repository: User repository dependency

    Returns:
        GetTodosUseCase: UseCase instance with injected dependencies
    """
    return GetTodosUseCase(todo_repository, user_repository)


def get_get_todo_by_id_usecase(
    todo_repository: TodoRepository = Depends(get_todo_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> GetTodoByIdUseCase:
    """Factory function for GetTodoByIdUseCase.

    Args:
        todo_repository: Todo repository dependency
        user_repository: User repository dependency

    Returns:
        GetTodoByIdUseCase: UseCase instance with injected dependencies
    """
    return GetTodoByIdUseCase(todo_repository, user_repository)


def get_update_todo_usecase(
    todo_repository: TodoRepository = Depends(get_todo_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> UpdateTodoUseCase:
    """Factory function for UpdateTodoUseCase.

    Args:
        todo_repository: Todo repository dependency
        user_repository: User repository dependency

    Returns:
        UpdateTodoUseCase: UseCase instance with injected dependencies
    """
    return UpdateTodoUseCase(todo_repository, user_repository)


def get_delete_todo_usecase(
    todo_repository: TodoRepository = Depends(get_todo_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> DeleteTodoUseCase:
    """Factory function for DeleteTodoUseCase.

    Args:
        todo_repository: Todo repository dependency
        user_repository: User repository dependency

    Returns:
        DeleteTodoUseCase: UseCase instance with injected dependencies
    """
    return DeleteTodoUseCase(todo_repository, user_repository)


# =============================================================================
# User UseCase Factory Functions
# =============================================================================


def get_create_user_usecase(
    user_repository: UserRepository = Depends(get_user_repository),
) -> CreateUserUseCase:
    """Factory function for CreateUserUseCase.

    Args:
        user_repository: User repository dependency

    Returns:
        CreateUserUseCase: UseCase instance with injected dependencies
    """
    return CreateUserUseCase(user_repository)


def get_get_users_usecase(
    user_repository: UserRepository = Depends(get_user_repository),
) -> GetUsersUseCase:
    """Factory function for GetUsersUseCase.

    Args:
        user_repository: User repository dependency

    Returns:
        GetUsersUseCase: UseCase instance with injected dependencies
    """
    return GetUsersUseCase(user_repository)


def get_get_user_by_id_usecase(
    user_repository: UserRepository = Depends(get_user_repository),
) -> GetUserByIdUseCase:
    """Factory function for GetUserByIdUseCase.

    Args:
        user_repository: User repository dependency

    Returns:
        GetUserByIdUseCase: UseCase instance with injected dependencies
    """
    return GetUserByIdUseCase(user_repository)


def get_update_user_usecase(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UpdateUserUseCase:
    """Factory function for UpdateUserUseCase.

    Args:
        user_repository: User repository dependency

    Returns:
        UpdateUserUseCase: UseCase instance with injected dependencies
    """
    return UpdateUserUseCase(user_repository)


def get_delete_user_usecase(
    user_repository: UserRepository = Depends(get_user_repository),
) -> DeleteUserUseCase:
    """Factory function for DeleteUserUseCase.

    Args:
        user_repository: User repository dependency

    Returns:
        DeleteUserUseCase: UseCase instance with injected dependencies
    """
    return DeleteUserUseCase(user_repository)
