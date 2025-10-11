"""tests/unit/usecase向け共通フィクスチャ"""

from unittest.mock import Mock

import pytest

from app.domain.services.transaction_manager import TransactionManager


class _AsyncNoopTransactionContext:
    async def __aenter__(self):
        return None

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.fixture
def mock_transaction_manager() -> Mock:
    transaction_manager = Mock(spec=TransactionManager)
    transaction_manager.begin_transaction.return_value = _AsyncNoopTransactionContext()
    return transaction_manager


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
