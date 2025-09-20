"""Exception handlers for FastAPI application.

This module contains all exception handlers that provide centralized
error handling, logging, and monitoring for the application.
"""

import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import BaseCustomException


async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all domain exceptions with unified logging and monitoring.

    This handler provides centralized handling for all domain-level exceptions
    including business rule violations and system errors, with appropriate
    logging levels and monitoring based on the exception type.
    """
    # Ensure we're handling a BaseCustomException
    if not isinstance(exc, BaseCustomException):
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )

    # Log with appropriate level based on exception type
    logger = logging.getLogger(__name__)
    log_level = getattr(logging, exc.get_log_level())

    # Log exception with stack trace using exc_info=True
    detail_message = f"Exception occurred: {exc}"
    logger.log(
        level=log_level,
        msg=detail_message,
        exc_info=True,
    )

    # Use the specific HTTP status code from the exception
    # API response contains only clean, user-friendly message (no stack trace)
    return JSONResponse(
        status_code=exc.http_status_code.value, content={"detail": str(exc)}
    )
