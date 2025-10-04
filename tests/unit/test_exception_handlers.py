import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.middleware.exception_handlers import register_exception_handlers
from app.domain.exceptions.base import ExceptionStatusCode
from app.domain.exceptions.business import BusinessRuleException
from app.domain.exceptions.system import SystemException

pytestmark = pytest.mark.anyio("asyncio")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class _SampleBusinessException(BusinessRuleException):
    def __init__(self, message: str = "Sample business error") -> None:
        super().__init__(message=message)

    @property
    def http_status_code(self) -> ExceptionStatusCode:
        return ExceptionStatusCode.VALIDATION_ERR


async def test_business_exception_handler_returns_warning_with_expected_response(
    caplog,
) -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    async def boom() -> None:
        raise _SampleBusinessException()

    caplog.set_level("WARNING")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/boom")

    # 例外クラスで設定したステータスコードでレスポンスされること
    assert response.status_code == ExceptionStatusCode.VALIDATION_ERR.value

    # 例外クラスで設定したメッセージがレスポンスされること
    assert response.json() == {"detail": "Sample business error"}

    # BusinessRuleExceptionのloglevelはWARNINGであること
    # 設定したメッセージがログに出力されること
    assert any(
        record.levelname == "WARNING"
        and "BuisinessException occurred: Sample business error" in record.msg
        for record in caplog.records
    )

    # Stack Traceがログに含まれていないこと
    assert "Traceback (most recent call last):" not in caplog.text


class _SampleSystemException(SystemException):
    def __init__(self, message: str = "Sample system error") -> None:
        super().__init__(message=message)

    @property
    def http_status_code(self) -> ExceptionStatusCode:
        return ExceptionStatusCode.SERVICE_UNAVAILABLE


async def test_system_exception_handler_returns_warning_with_expected_response(
    caplog,
) -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    async def boom() -> None:
        raise _SampleSystemException()

    caplog.set_level("ERROR")

    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/boom")

    # 例外クラスで設定したステータスコードでレスポンスされること
    assert response.status_code == ExceptionStatusCode.SERVICE_UNAVAILABLE.value

    # 例外クラスで設定したメッセージがレスポンスされること
    assert response.json() == {"detail": "Sample system error"}

    # SystemException occurredがログに表示されること
    assert any(
        record.levelname == "ERROR"
        and "SystemException occurred: Sample system error" in record.msg
        for record in caplog.records
    )

    # Stack Traceがログに含まれていること
    assert "Traceback (most recent call last):" in caplog.text
