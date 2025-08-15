"""Dependency Injection configuration for the entire application.

This is the Composition Root - the only layer allowed to depend on all other layers.
It assembles concrete implementations and provides factory functions for FastAPI DI.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.todo_repository import TodoRepository
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.sqlalchemy_todo_repository import (
    SQLAlchemyTodoRepository,
)
from app.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from app.infrastructure.services.sqlalchemy_transaction_manager import (
    SQLAlchemyTransactionManager,
)
from app.usecases.todo.create_todo_usecase import CreateTodoUseCase
from app.usecases.todo.delete_todo_usecase import DeleteTodoUseCase
from app.usecases.todo.get_todo_by_id_usecase import GetTodoByIdUseCase
from app.usecases.todo.get_todos_usecase import GetTodosUseCase
from app.usecases.todo.update_todo_usecase import UpdateTodoUseCase
from app.usecases.user.create_user_usecase import CreateUserUseCase
from app.usecases.user.delete_user_usecase import DeleteUserUseCase
from app.usecases.user.get_user_by_id_usecase import GetUserByIdUseCase
from app.usecases.user.get_users_usecase import GetUsersUseCase
from app.usecases.user.update_user_usecase import UpdateUserUseCase

# =============================================================================
# Repository Factory Functions
# =============================================================================


def get_todo_repository(db: AsyncSession = Depends(get_db)) -> TodoRepository:
    """Factory function for TodoRepository.

    Args:
        db: Database session dependency

    Returns:
        TodoRepository: Concrete repository implementation
    """
    return SQLAlchemyTodoRepository(db)


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """Factory function for UserRepository.

    Args:
        db: Database session dependency

    Returns:
        UserRepository: Concrete repository implementation
    """
    return SQLAlchemyUserRepository(db)


# =============================================================================
# Transaction-managed Repository Factory Functions (Deprecated)
# Note: Transaction management is now handled at UseCase layer
# =============================================================================


# =============================================================================
# Todo UseCase Factory Functions
# =============================================================================


def get_create_todo_usecase(db: AsyncSession = Depends(get_db)) -> CreateTodoUseCase:
    """Factory function for CreateTodoUseCase.

    Transaction management is handled within the UseCase layer.

    Args:
        db: Database session dependency

    Returns:
        CreateTodoUseCase: UseCase instance with injected dependencies
    """
    transaction_manager = SQLAlchemyTransactionManager(db)
    todo_repository = SQLAlchemyTodoRepository(db)
    user_repository = SQLAlchemyUserRepository(db)
    return CreateTodoUseCase(transaction_manager, todo_repository, user_repository)


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


def get_update_todo_usecase(db: AsyncSession = Depends(get_db)) -> UpdateTodoUseCase:
    """Factory function for UpdateTodoUseCase.

    Transaction management is handled within the UseCase layer.

    Args:
        db: Database session dependency

    Returns:
        UpdateTodoUseCase: UseCase instance with injected dependencies
    """
    transaction_manager = SQLAlchemyTransactionManager(db)
    todo_repository = SQLAlchemyTodoRepository(db)
    user_repository = SQLAlchemyUserRepository(db)
    return UpdateTodoUseCase(transaction_manager, todo_repository, user_repository)


def get_delete_todo_usecase(db: AsyncSession = Depends(get_db)) -> DeleteTodoUseCase:
    """Factory function for DeleteTodoUseCase.

    Transaction management is handled within the UseCase layer.

    Args:
        db: Database session dependency

    Returns:
        DeleteTodoUseCase: UseCase instance with injected dependencies
    """
    transaction_manager = SQLAlchemyTransactionManager(db)
    todo_repository = SQLAlchemyTodoRepository(db)
    user_repository = SQLAlchemyUserRepository(db)
    return DeleteTodoUseCase(transaction_manager, todo_repository, user_repository)


# =============================================================================
# User UseCase Factory Functions
# =============================================================================


def get_create_user_usecase(db: AsyncSession = Depends(get_db)) -> CreateUserUseCase:
    """Factory function for CreateUserUseCase.

    Transaction management is handled within the UseCase layer.

    Args:
        db: Database session dependency

    Returns:
        CreateUserUseCase: UseCase instance with injected dependencies
    """
    transaction_manager = SQLAlchemyTransactionManager(db)
    user_repository = SQLAlchemyUserRepository(db)
    return CreateUserUseCase(transaction_manager, user_repository)


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


def get_update_user_usecase(db: AsyncSession = Depends(get_db)) -> UpdateUserUseCase:
    """Factory function for UpdateUserUseCase.

    Transaction management is handled within the UseCase layer.

    Args:
        db: Database session dependency

    Returns:
        UpdateUserUseCase: UseCase instance with injected dependencies
    """
    transaction_manager = SQLAlchemyTransactionManager(db)
    user_repository = SQLAlchemyUserRepository(db)
    return UpdateUserUseCase(transaction_manager, user_repository)


def get_delete_user_usecase(db: AsyncSession = Depends(get_db)) -> DeleteUserUseCase:
    """Factory function for DeleteUserUseCase.

    Transaction management is handled within the UseCase layer.

    Args:
        db: Database session dependency

    Returns:
        DeleteUserUseCase: UseCase instance with injected dependencies
    """
    transaction_manager = SQLAlchemyTransactionManager(db)
    user_repository = SQLAlchemyUserRepository(db)
    return DeleteUserUseCase(transaction_manager, user_repository)
