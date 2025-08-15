"""SQLAlchemy implementation of Transaction Manager."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.services.transaction_manager import TransactionManager


class SQLAlchemyTransactionManager(TransactionManager):
    """SQLAlchemy implementation of TransactionManager."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session.

        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    def begin_transaction(self) -> Any:  # Returns AsyncSessionTransaction
        """Begin a database transaction using SQLAlchemy session.

        Returns:
            AsyncContextManager for transaction scope

        Note:
            Automatically commits on success or rolls back on exception.
        """
        return self.db.begin()
