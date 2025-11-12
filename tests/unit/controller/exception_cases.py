from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from app.domain.exceptions.business import UserNotFoundException, ValidationException
from app.domain.exceptions.system import DataOperationException


@dataclass(frozen=True)
class ControllerExceptionCase:
    """Reusable controller-layer exception scenario."""

    id: str
    factory: Callable[[], Exception]


def controller_domain_exception_cases() -> Sequence[ControllerExceptionCase]:
    """Return representative domain exceptions controllers must propagate."""

    return (
        ControllerExceptionCase(
            id="validation_error",
            factory=lambda: ValidationException("invalid input", "field"),
        ),
        ControllerExceptionCase(
            id="user_not_found",
            factory=lambda: UserNotFoundException(user_id=999),
        ),
        ControllerExceptionCase(
            id="data_operation_error",
            factory=lambda: DataOperationException(
                operation_name="GenericRepository.save"
            ),
        ),
    )
