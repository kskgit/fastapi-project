"""Exception handlers for FastAPI application.

This module contains all exception handlers that provide centralized
error handling, logging, and monitoring for the application.
"""

import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar, cast

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, Response

from app.domain.exceptions.base import BaseCustomException
from app.domain.exceptions.business import BusinessRuleException
from app.domain.exceptions.system import SystemException

DomainExceptionT = TypeVar("DomainExceptionT", bound=BaseCustomException)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers for the FastAPI application."""

    def _register_domain_exception_handler(
        exception_cls: type[DomainExceptionT],
    ) -> None:
        async def _handler(request: Request, exc: DomainExceptionT) -> Response:
            logger = logging.getLogger(__name__)

            log_level = getattr(logging, exc.get_log_level())
            detail_message = f"{exc.get_log_prefix()}: {exc}"

            logger.log(
                level=log_level,
                msg=detail_message,
                exc_info=exc.include_exc_info(),
            )

            return JSONResponse(
                status_code=exc.http_status_code.value,
                content={"detail": exc.get_user_message()},
            )

        app.add_exception_handler(
            exception_cls,
            cast(
                Callable[[Request, Exception], Awaitable[Response]],
                _handler,
            ),
        )

    _register_domain_exception_handler(BusinessRuleException)
    _register_domain_exception_handler(SystemException)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> Response:
        """Handle unexpected exceptions with structured logging."""

        logger = logging.getLogger(__name__)

        detail_message = f"Exception occurred: {exc}"
        logger.log(
            level=logging.CRITICAL,
            msg=detail_message,
            exc_info=True,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "INTERNAL_SERVER_ERROR"},
        )
