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
    # システムエラー・内部サーバーエラー
    INTERNAL_SERVER_ERROR = 500
    # サービス一時的に利用不可
    SERVICE_UNAVAILABLE = 503


class BaseCustomException(Exception, ABC):
    """共通のユーザ定義例外."""

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

    @property
    def log_level(self) -> str:
        """Get log level for this domain exception.

        Returns:
            str: Log level appropriate for the exception type
        Note:
            Should be overridden by subclasses to return appropriate level
        """
        raise NotImplementedError("Subclasses must implement log_level property")

    @property
    def user_message(self) -> str:
        """Get user-friendly message for API response.

        Returns:
            str: User-safe error message without internal implementation details

        Note:
            By default returns the internal message. Subclasses should override
            this method to provide secure, user-friendly messages.
        """
        return str(self)


    @property
    def http_status_code(self) -> ExceptionStatusCode:
        """Get HTTP status code for API response.

        Returns:
            BusinessRuleExceptionStatusCode: HTTP status code

        Note:
            Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement http_status_code property")
