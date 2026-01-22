"""Shared dependency providers for repositories and infrastructure services."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.subtask_repository import SubTaskRepository
from app.domain.repositories.todo_repository import TodoRepository
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.sqlalchemy_subtask_repository import (
    SQLAlchemySubTaskRepository,
)
from app.infrastructure.repositories.sqlalchemy_todo_repository import (
    SQLAlchemyTodoRepository,
)
from app.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from app.infrastructure.services.sqlalchemy_transaction_manager import (
    SQLAlchemyTransactionManager,
)


def get_todo_repository(db: AsyncSession = Depends(get_db)) -> TodoRepository:
    """Factory function for TodoRepository."""
    return SQLAlchemyTodoRepository(db)


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """Factory function for UserRepository."""
    return SQLAlchemyUserRepository(db)


def get_transaction_manager(
    db: AsyncSession = Depends(get_db),
) -> SQLAlchemyTransactionManager:
    """Factory function for TransactionManager."""
    return SQLAlchemyTransactionManager(db)



def get_subtask_repository(
    db: AsyncSession = Depends(get_db),
) -> SubTaskRepository:
    """Factory function for SubTaskRepository."""
    return SQLAlchemySubTaskRepository(db)
