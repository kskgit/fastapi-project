"""Shared dependency providers for repositories and infrastructure services."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import SubTaskRepository, TodoRepository, UserRepository
from app.infrastructure.database import get_db
from app.infrastructure.repositories import (
    SQLAlchemySubTaskRepository,
    SQLAlchemyTodoRepository,
    SQLAlchemyUserRepository,
)
from app.infrastructure.services import SQLAlchemyTransactionManager


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
