"""
Moodify SDK Exceptions

Custom exceptions for error handling.
"""

from typing import Any, Dict, Optional


class MoodifyError(Exception):
    """
    Base exception for Moodify SDK.

    Attributes:
        message: Error message
        code: Error code
        details: Additional error details
    """

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code or "unknown_error"
        self.details = details or {}

    def __str__(self) -> str:
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "error": self.message,
            "code": self.code,
            "details": self.details
        }


class APIError(MoodifyError):
    """
    API request failed.

    Attributes:
        status_code: HTTP status code
        response_body: Raw response body
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        response_body: Optional[str] = None,
        code: Optional[str] = None
    ):
        super().__init__(message, code or f"http_{status_code}")
        self.status_code = status_code
        self.response_body = response_body

    def __str__(self) -> str:
        return f"API Error {self.status_code}: {self.message}"


class ValidationError(MoodifyError):
    """
    Input validation failed.

    Raised when:
    - File not found
    - Invalid file format
    - Missing required parameters
    - Invalid parameter values
    """

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, code="validation_error")
        self.field = field

    def __str__(self) -> str:
        if self.field:
            return f"Validation Error ({self.field}): {self.message}"
        return f"Validation Error: {self.message}"


class AuthenticationError(MoodifyError):
    """
    Authentication failed.

    Raised when:
    - API key is invalid
    - API key is expired
    - Missing authentication
    - Insufficient permissions
    """

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, code="authentication_error")


class RateLimitError(APIError):
    """
    Rate limit exceeded.

    Attributes:
        retry_after: Seconds to wait before retry
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None
    ):
        super().__init__(message, status_code=429, code="rate_limit")
        self.retry_after = retry_after

    def __str__(self) -> str:
        if self.retry_after:
            return f"Rate limit exceeded. Retry after {self.retry_after} seconds."
        return self.message


class ServerError(APIError):
    """
    Server error (5xx).

    Raised when Moodify API returns server error.
    """

    def __init__(self, message: str = "Server error", status_code: int = 500):
        super().__init__(message, status_code, code="server_error")


class TimeoutError(MoodifyError):
    """
    Request timeout.

    Raised when request exceeds timeout limit.
    """

    def __init__(self, message: str = "Request timeout", timeout: Optional[float] = None):
        super().__init__(message, code="timeout")
        self.timeout = timeout


class ConnectionError(MoodifyError):
    """
    Connection failed.

    Raised when unable to connect to API.
    """

    def __init__(self, message: str = "Failed to connect to API"):
        super().__init__(message, code="connection_error")


class ProcessingError(MoodifyError):
    """
    Audio processing failed.

    Raised when audio processing operation fails.
    """

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code="processing_error", details=details)
        self.operation = operation


class NotFoundError(APIError):
    """
    Resource not found.

    Raised when requested resource does not exist.
    """

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404, code="not_found")


class ConflictError(APIError):
    """
    Resource conflict.

    Raised when request conflicts with existing state.
    """

    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status_code=409, code="conflict")


# Error code mapping for HTTP status codes
HTTP_ERROR_CODES = {
    400: ValidationError,
    401: AuthenticationError,
    403: AuthenticationError,
    404: NotFoundError,
    409: ConflictError,
    429: RateLimitError,
    500: ServerError,
    502: ServerError,
    503: ServerError,
    504: ServerError,
}


def raise_for_status(status_code: int, message: str, response_body: Optional[str] = None):
    """Raise appropriate exception based on status code."""
    error_class = HTTP_ERROR_CODES.get(status_code, APIError)
    raise error_class(message=message, status_code=status_code, response_body=response_body)
