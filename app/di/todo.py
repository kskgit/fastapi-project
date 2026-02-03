"""Dependency Injection configuration for the entire application.

This remains the composition root for Todo-related dependencies and shared wiring.
User-specific providers live in app.di.user to keep this module focused.
"""

from fastapi import Depends

from app.di.common import (
    get_subtask_repository,
    get_todo_repository,
    get_transaction_manager,
    get_user_repository,
)
from app.di.user import get_user_domain_service
from app.domain.repositories import SubTaskRepository, TodoRepository, UserRepository
from app.domain.services import UserDomainService
from app.infrastructure.services import SQLAlchemyTransactionManager
from app.usecases.todo import (
    CreateTodoUseCase,
    DeleteTodoUseCase,
    GetTodoByIdUseCase,
    GetTodosUseCase,
    UpdateTodoUseCase,
)


def get_create_todo_usecase(
    transaction_manager: SQLAlchemyTransactionManager = Depends(
        get_transaction_manager
    ),
    todo_repository: TodoRepository = Depends(get_todo_repository),
    user_repository: UserRepository = Depends(get_user_repository),
    user_domain_service: UserDomainService = Depends(get_user_domain_service),
) -> CreateTodoUseCase:
    """Factory function for CreateTodoUseCase.

    Transaction management is handled within the UseCase layer.
    """
    return CreateTodoUseCase(
        transaction_manager,
        todo_repository,
        user_repository,
        user_domain_service,
    )


def get_get_todos_usecase(
    todo_repository: TodoRepository = Depends(get_todo_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> GetTodosUseCase:
    """Factory function for GetTodosUseCase."""
    return GetTodosUseCase(todo_repository, user_repository)


def get_get_todo_by_id_usecase(
    todo_repository: TodoRepository = Depends(get_todo_repository),
    user_repository: UserRepository = Depends(get_user_repository),
    subtask_repository: SubTaskRepository = Depends(get_subtask_repository),
) -> GetTodoByIdUseCase:
    """Factory function for GetTodoByIdUseCase."""
    return GetTodoByIdUseCase(todo_repository, user_repository, subtask_repository)


def get_update_todo_usecase(
    transaction_manager: SQLAlchemyTransactionManager = Depends(
        get_transaction_manager
    ),
    todo_repository: TodoRepository = Depends(get_todo_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> UpdateTodoUseCase:
    """Factory function for UpdateTodoUseCase."""
    return UpdateTodoUseCase(transaction_manager, todo_repository, user_repository)


def get_delete_todo_usecase(
    transaction_manager: SQLAlchemyTransactionManager = Depends(
        get_transaction_manager
    ),
    todo_repository: TodoRepository = Depends(get_todo_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> DeleteTodoUseCase:
    """Factory function for DeleteTodoUseCase."""
    return DeleteTodoUseCase(transaction_manager, todo_repository, user_repository)
