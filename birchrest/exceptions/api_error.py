from typing import Type

from birchrest.http.response import Response
from birchrest.http.status import HttpStatus


class ApiError(Exception):
    """
    A custom exception class used to represent API errors. Each error has a status code,
    a user-friendly message, and a base message (from the HTTP status code description).
    It can also convert itself into an HTTP response.
    """

    def __init__(self, user_message: str, status_code: int) -> None:
        """
        Initialize the ApiError with a user message and an HTTP status code.

        Args:
            user_message (str): A message explaining the error, meant for users.
            status_code (int): The HTTP status code that describes the error.
        """

        super().__init__(user_message)
        self.base_message: str = HttpStatus.description(status_code)
        self.user_message: str = user_message
        self.status_code: int = status_code

    def __str__(self) -> str:
        """
        Return a string representation of the error with the status code and user message.

        Returns:
            str: A formatted string showing the status code and the user-friendly message.
        """

        return f"[{self.status_code}] {self.user_message}"

    def convert_to_response(self, res: Response) -> Response:
        """
        Convert the ApiError into an HTTP response object.

        Args:
            res (Response): The HTTP response object to send back to the client.

        Returns:
            Response: The HTTP response with the error details, status code, and correlation ID.
        """

        payload = {
            "error": {
                "status": self.status_code,
                "code": self.base_message,
                "correlationId": res.correlation_id,
            }
        }

        if self.user_message:
            payload["error"]["message"] = self.user_message

        return res.status(self.status_code).send(payload)


class BadRequest(ApiError):
    """
    Represents a 400 Bad Request error.
    """

    def __init__(self, user_message: str = ""):
        super().__init__(user_message, 400)


class Unauthorized(ApiError):
    """
    Represents a 401 Unauthorized error.
    """

    def __init__(self, user_message: str = ""):
        super().__init__(user_message, 401)


class Forbidden(ApiError):
    """
    Represents a 403 Forbidden error.
    """

    def __init__(self, user_message: str = ""):
        super().__init__(user_message, 403)


class NotFound(ApiError):
    """
    Represents a 404 Not Found error.
    """

    def __init__(self, user_message: str = ""):
        super().__init__(user_message, 404)


class Conflict(ApiError):
    """
    Represents a 409 Conflict error.
    """

    def __init__(self, user_message: str = ""):
        super().__init__(user_message, 409)


class InternalServerError(ApiError):
    """
    Represents a 500 Internal Server Error.
    """

    def __init__(self, user_message: str = ""):
        super().__init__(user_message, 500)


class ServiceUnavailable(ApiError):
    """
    Represents a 503 Service Unavailable error.
    """

    def __init__(self, user_message: str = ""):
        super().__init__(user_message, 503)


class MethodNotAllowed(ApiError):
    """
    Represents a 405 Method Not Allowed error.
    """

    def __init__(self, user_message: str = ""):
        super().__init__(user_message, 405)


class UnprocessableEntity(ApiError):
    """
    Represents a 422 Unprocessable Entity error.
    """

    def __init__(self, user_message: str = ""):
        super().__init__(user_message, 422)


class PaymentRequired(ApiError):
    """
    Represents a 402 Payment Required error.
    """

    def __init__(self, user_message: str = ""):
        super().__init__(user_message, 402)


class RequestTimeout(ApiError):
    """
    Represents a 408 Request Timeout error.
    """

    def __init__(self, user_message: str = ""):
        super().__init__(user_message, 408)


class Gone(ApiError):
    """
    Represents a 410 Gone error.
    """

    def __init__(self, user_message: str = ""):
        super().__init__(user_message, 410)


class LengthRequired(ApiError):
    """
    Represents a 411 Length Required error.
    """

    def __init__(self, user_message: str = ""):
        super().__init__(user_message, 411)


class PreconditionFailed(ApiError):
    """
    Represents a 412 Precondition Failed error.
    """

    def __init__(self, user_message: str = ""):
        super().__init__(user_message, 412)


class PayloadTooLarge(ApiError):
    """
    Represents a 413 Payload Too Large error.
    """

    def __init__(self, user_message: str = ""):
        super().__init__(user_message, 413)


class UnsupportedMediaType(ApiError):
    """
    Represents a 415 Unsupported Media Type error.
    """

    def __init__(self, user_message: str = ""):
        super().__init__(user_message, 415)


class TooManyRequests(ApiError):
    """
    Represents a 429 Too Many Requests error.
    """

    def __init__(self, user_message: str = ""):
        super().__init__(user_message, 429)


class UpgradeRequired(ApiError):
    """
    Represents a 426 Upgrade Required error.
    """

    def __init__(self, user_message: str = ""):
        super().__init__(user_message, 426)
