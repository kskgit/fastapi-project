"""Exception handlers for FastAPI application.

This module contains all exception handlers that provide centralized
error handling, logging, and monitoring for the application.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, Response

from app.domain.exceptions.business import BusinessRuleException
from app.domain.exceptions.system import SystemException


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers for the FastAPI application."""

    @app.exception_handler(BusinessRuleException)
    async def business_exception_handler(
        request: Request, exc: BusinessRuleException
    ) -> Response:
        """Handle domain exceptions with structured logging and responses."""

        logger = logging.getLogger(__name__)

        log_level = getattr(logging, exc.get_log_level())

        detail_message = f"BuisinessException occurred: {exc}"
        logger.log(
            level=log_level,
            msg=detail_message,
        )

        return JSONResponse(
            status_code=exc.http_status_code.value,
            content={"detail": exc.get_user_message()},
        )

    @app.exception_handler(SystemException)
    async def system_exception_handler(
        request: Request, exc: SystemException
    ) -> Response:
        """Handle domain exceptions with structured logging and responses."""

        logger = logging.getLogger(__name__)

        log_level = getattr(logging, exc.get_log_level())

        detail_message = f"SystemException occurred: {exc}"
        logger.log(
            level=log_level,
            msg=detail_message,
            exc_info=True,
        )

        return JSONResponse(
            status_code=exc.http_status_code.value,
            content={"detail": exc.get_user_message()},
        )

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
