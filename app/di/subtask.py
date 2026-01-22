from fastapi import Depends

from app.di.common import (
    get_subtask_repository,
    get_todo_repository,
    get_transaction_manager,
    get_user_repository,
)
from app.domain.repositories.subtask_repository import SubTaskRepository
from app.domain.repositories.todo_repository import TodoRepository
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.subtask_domain_service import SubTaskDomainService
from app.infrastructure.services.sqlalchemy_transaction_manager import (
    SQLAlchemyTransactionManager,
)
from app.usecases.subtask.create_subtask_usecase import CreateSubTaskUseCase


def get_subtask_domain_service() -> SubTaskDomainService:
    return SubTaskDomainService()


def get_create_subtask_usecase(
    transaction_manager: SQLAlchemyTransactionManager = Depends(
        get_transaction_manager
    ),
    user_repository: UserRepository = Depends(get_user_repository),
    todo_repository: TodoRepository = Depends(get_todo_repository),
    subtask_domain_service: SubTaskDomainService = Depends(get_subtask_domain_service),
    subtask_repository: SubTaskRepository = Depends(get_subtask_repository),
) -> CreateSubTaskUseCase:
    return CreateSubTaskUseCase(
        user_repository=user_repository,
        todo_repository=todo_repository,
        subtask_domain_service=subtask_domain_service,
        transaction_manager=transaction_manager,
        subtask_repository=subtask_repository
    )
