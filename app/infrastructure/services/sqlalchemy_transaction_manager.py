"""SQLAlchemy implementation of Transaction Manager."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.transaction_manager import TransactionManager


class SQLAlchemyTransactionManager(TransactionManager):
    """SQLAlchemy implementation of TransactionManager."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session.

        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    def begin_transaction(self) -> Any:
        """Begin a database transaction using SQLAlchemy session.

        Returns:
            AsyncContextManager for transaction scope

        Note:
            Handles SQLAlchemy's auto-transaction behavior properly.
            If a transaction is already active, uses nested transaction.
            Otherwise, starts a new transaction.
        """
        return self._transaction_context()

    @asynccontextmanager
    async def _transaction_context(self) -> AsyncGenerator[None, None]:
        """Context manager for transaction handling.

        Handles both new transactions and nested transactions properly.
        """
        if self.db.in_transaction():
            # Session already has an active transaction, use nested transaction
            async with self.db.begin_nested() as savepoint:
                try:
                    yield
                    await savepoint.commit()
                except Exception:
                    await savepoint.rollback()
                    raise
        else:
            # No active transaction, start a new one
            async with self.db.begin() as transaction:
                try:
                    yield
                    await transaction.commit()
                except Exception:
                    await transaction.rollback()
                    raise
