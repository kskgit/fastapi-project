"""Core middleware module for FastAPI application.

This module contains middleware components that are essential for the
application's core functionality and system-level concerns.
"""

from .exception_handlers import register_exception_handlers

__all__ = [
    "register_exception_handlers",
]
