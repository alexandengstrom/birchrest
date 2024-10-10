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

    @staticmethod
    def BAD_REQUEST(user_message: str = "") -> "ApiError":
        """
        Create a 400 Bad Request error.

        Args:
            user_message (str, optional): Custom message for the error. Defaults to an empty string.

        Returns:
            ApiError: The generated Bad Request error.
        """

        return ApiError(user_message, 400)

    @staticmethod
    def UNAUTHORIZED(user_message: str = "") -> "ApiError":
        """
        Create a 401 Unauthorized error.

        Args:
            user_message (str, optional): Custom message for the error. Defaults to an empty string.

        Returns:
            ApiError: The generated Unauthorized error.
        """

        return ApiError(user_message, 401)

    @staticmethod
    def FORBIDDEN(user_message: str = "") -> "ApiError":
        """
        Create a 403 Forbidden error.

        Args:
            user_message (str, optional): Custom message for the error. Defaults to an empty string.

        Returns:
            ApiError: The generated Forbidden error.
        """

        return ApiError(user_message, 403)

    @staticmethod
    def NOT_FOUND(user_message: str = "") -> "ApiError":
        """
        Create a 404 Not Found error.

        Args:
            user_message (str, optional): Custom message for the error. Defaults to an empty string.

        Returns:
            ApiError: The generated Not Found error.
        """

        return ApiError(user_message, 404)

    @staticmethod
    def METHOD_NOT_ALLOWED(user_message: str = "") -> "ApiError":
        """
        Create a 405 Method Not Allowed error.

        Args:
            user_message (str, optional): Custom message for the error. Defaults to an empty string.

        Returns:
            ApiError: The generated Method Not Allowed error.
        """

        return ApiError(user_message, 405)

    @staticmethod
    def INTERNAL_SERVER_ERROR(user_message: str = "") -> "ApiError":
        """
        Create a 500 Internal Server Error.

        Args:
            user_message (str, optional): Custom message for the error. Defaults to an empty string.

        Returns:
            ApiError: The generated Internal Server Error.
        """

        return ApiError(user_message, 500)
