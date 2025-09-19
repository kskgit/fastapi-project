"""Exception handlers for FastAPI application.

This module contains all exception handlers that provide centralized
error handling, logging, and monitoring for the application.
"""

import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import BaseCustomException


async def domain_exception_handler(request: Request, exc: Exception) -> JSONResponse:
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

    # Add structured logging context
    extra_context = {
        "exception_type": exc.__class__.__name__,
        "error_category": exc.get_error_category(),
        "should_trigger_alert": exc.should_trigger_alert(),
        "request_path": request.url.path,
    }

    # Include original stack trace if available in exception details
    if hasattr(exc, "details") and exc.details and "stack_trace" in exc.details:
        extra_context["stack_trace"] = exc.details["stack_trace"]

    # Include details if available (for SystemException)
    if hasattr(exc, "details") and exc.details:
        extra_context["details"] = exc.details
    if hasattr(exc, "error_code"):
        extra_context["error_code"] = exc.error_code

    # Log exception with stack trace
    detail_message = f"Exception occurred: {exc}"
    if extra_context.get("stack_trace"):
        detail_message += f"\nStack trace:\n{extra_context['stack_trace']}"

    logger.log(level=log_level, msg=detail_message, extra=extra_context)

    # Use the specific HTTP status code from the exception
    # API response contains only clean, user-friendly message (no stack trace)
    return JSONResponse(
        status_code=exc.http_status_code.value, content={"detail": str(exc)}
    )
