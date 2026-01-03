from fastapi import Depends

from app.di.common import get_transaction_manager
from app.infrastructure.services.sqlalchemy_transaction_manager import (
    SQLAlchemyTransactionManager,
)
from app.usecases.subtask.create_subtask_usecase import CreateSubTaskUseCase


def get_create_subtask_usecase(
    transaction_manager: SQLAlchemyTransactionManager = Depends(
        get_transaction_manager
    ),
) -> CreateSubTaskUseCase:
    return CreateSubTaskUseCase(
        transaction_manager=transaction_manager,
    )
