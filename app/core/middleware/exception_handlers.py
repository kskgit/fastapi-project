"""Exception handlers for FastAPI application.

This module contains all exception handlers that provide centralized
error handling, logging, and monitoring for the application.
"""

import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse, Response

from app.domain.exceptions import BaseCustomException
from main import app


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> Response:
    """Adapter that ensures FastAPI-compatible signature for custom handler."""

    logger = logging.getLogger(__name__)

    detail_message = f"Exception occurred: {exc}"
    logger.log(
        level=logging.CRITICAL,
        msg=detail_message,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "INTERNAL_SERVER_ERROR"},
    )


@app.exception_handler(BaseCustomException)
async def custom_exception_handler(
    request: Request, exc: BaseCustomException
) -> Response:
    """Adapter that ensures FastAPI-compatible signature for custom handler."""

    logger = logging.getLogger(__name__)

    log_level = getattr(logging, exc.get_log_level())

    detail_message = f"Exception occurred: {exc}"
    logger.log(
        level=log_level,
        msg=detail_message,
    )

    return JSONResponse(
        status_code=exc.http_status_code.value,
        content={"detail": exc.get_user_message()},
    )
