from abc import ABC
from enum import Enum
from typing import Any


class ExceptionStatusCode(Enum):
    # 処理実行前にリクエスト内容の不備で処理が実行できない
    VALIDATION_ERR = 400
    # 処理対象のリソースが見つからない
    NOT_FOUND = 404
    # ビジネスロジックの制約で処理が実行出来ない
    UNPROCESSABLE_ENTITY = 422


class BaseUserException(Exception, ABC):
    """Base exception for all business rule violations.

    This exception provides unified handling for all types of business logic
    errors with consistent logging levels and monitoring behavior, while
    allowing subclasses to define appropriate HTTP status codes.

    Business rule violations are considered user-caused errors that:
    - Should be logged at WARNING level (not ERROR)
    - Should not trigger operational alerts
    - Should provide clear user-facing error messages
    """

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize business rule exception.

        Args:
            message: Human-readable error message
            details: Additional context information about the violation
        """
        super().__init__(message)
        self.details = details or {}

    def get_log_level(self) -> str:
        """Get log level for this business rule violation.

        Returns:
            str: Always 'WARNING' for business rule violations
        """
        return "WARNING"

    def should_trigger_alert(self) -> bool:
        """Check if this error should trigger operational alerts.

        Returns:
            bool: Always False for business rule violations
        """
        return False

    def get_error_category(self) -> str:
        """Get error category for metrics and monitoring.

        Returns:
            str: Error category for classification
        """
        return "business_rule_violation"

    @property
    def http_status_code(self) -> ExceptionStatusCode:
        """Get HTTP status code for API response.

        Returns:
            BusinessRuleExceptionStatusCode: HTTP status code

        Note:
            Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement http_status_code property")
