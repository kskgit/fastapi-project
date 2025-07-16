"""Todo endpoints dependency injection.

This module contains factory functions for Todo-related UseCases.
These functions will be used by FastAPI's dependency injection system.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.clean.core.database_clean import get_db
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


def get_create_todo_usecase(db: Session = Depends(get_db)) -> CreateTodoUseCase:
    """Factory function for CreateTodoUseCase.

    Creates UseCase instance with required repository dependencies.

    Args:
        db: Database session dependency

    Returns:
        CreateTodoUseCase: UseCase instance with injected dependencies
    """
    todo_repository = SQLAlchemyTodoRepository(db)
    user_repository = SQLAlchemyUserRepository(db)
    return CreateTodoUseCase(todo_repository, user_repository)


def get_get_todos_usecase(db: Session = Depends(get_db)) -> GetTodosUseCase:
    """Factory function for GetTodosUseCase.

    Creates UseCase instance with required repository dependencies.

    Args:
        db: Database session dependency

    Returns:
        GetTodosUseCase: UseCase instance with injected dependencies
    """
    todo_repository = SQLAlchemyTodoRepository(db)
    user_repository = SQLAlchemyUserRepository(db)
    return GetTodosUseCase(todo_repository, user_repository)


def get_get_todo_by_id_usecase(db: Session = Depends(get_db)) -> GetTodoByIdUseCase:
    """Factory function for GetTodoByIdUseCase.

    Creates UseCase instance with required repository dependencies.

    Args:
        db: Database session dependency

    Returns:
        GetTodoByIdUseCase: UseCase instance with injected dependencies
    """
    todo_repository = SQLAlchemyTodoRepository(db)
    user_repository = SQLAlchemyUserRepository(db)
    return GetTodoByIdUseCase(todo_repository, user_repository)


def get_update_todo_usecase(db: Session = Depends(get_db)) -> UpdateTodoUseCase:
    """Factory function for UpdateTodoUseCase.

    Creates UseCase instance with required repository dependencies.

    Args:
        db: Database session dependency

    Returns:
        UpdateTodoUseCase: UseCase instance with injected dependencies
    """
    todo_repository = SQLAlchemyTodoRepository(db)
    user_repository = SQLAlchemyUserRepository(db)
    return UpdateTodoUseCase(todo_repository, user_repository)


def get_delete_todo_usecase(db: Session = Depends(get_db)) -> DeleteTodoUseCase:
    """Factory function for DeleteTodoUseCase.

    Creates UseCase instance with required repository dependencies.

    Args:
        db: Database session dependency

    Returns:
        DeleteTodoUseCase: UseCase instance with injected dependencies
    """
    todo_repository = SQLAlchemyTodoRepository(db)
    user_repository = SQLAlchemyUserRepository(db)
    return DeleteTodoUseCase(todo_repository, user_repository)
