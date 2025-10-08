"""Exception handlers for FastAPI application.

This module contains all exception handlers that provide centralized
error handling, logging, and monitoring for the application.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, Response

from app.domain.exceptions.base import BaseCustomException


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers for the FastAPI application."""

    @app.exception_handler(BaseCustomException)
    async def custom_exception_handler(
        request: Request, exc: BaseCustomException
    ) -> Response:
        """Handle business domain exceptions."""

        logger = logging.getLogger(__name__)

        log_level = getattr(logging, exc.log_level)

        detail_message = f"{exc.log_prefix}: {exc}"
        logger.log(
            level=log_level,
            msg=detail_message,
            exc_info=exc.include_exc_info,
        )

        return JSONResponse(
            status_code=exc.http_status_code.value,
            content={"detail": exc.user_message},
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
