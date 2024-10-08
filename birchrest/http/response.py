import json
from typing import Dict, Any
from .status import HttpStatus


class Response:
    def __init__(self) -> None:
        """
        Initializes a new Response object with default values.
        """
        self._status_code: int = 200
        self._headers: Dict[str, str] = {'Content-Type': 'text/html'}
        self._body: str = ''
        self._is_sent: bool = False

    def status(self, code: int) -> 'Response':
        """
        Set the HTTP status code.

        :param code: The HTTP status code
        :return: self to allow for chaining
        """

        if isinstance(code, HttpStatus):
            self._status_code = code.value
        else:
            self._status_code = code
        return self

    def set_header(self, name: str, value: str) -> 'Response':
        """
        Set an HTTP header.

        :param name: The name of the header
        :param value: The value of the header
        :return: self to allow for chaining
        """
        self._headers[name] = value
        return self

    def send(self, data: Any = {}) -> 'Response':
        """
        Set the response body to a JSON-encoded string and set
        Content-Type to application/json.

        :param data: A dictionary to be JSON-encoded
        :return: self to allow for chaining
        """
        
        if self._is_sent:
            raise Exception("Request was sent twice")
        
        self._body = json.dumps(data)
        self.set_header('Content-Type', 'application/json')
        self._headers['Content-Length'] = str(len(self._body))
        self._is_sent = True
        return self

    def end(self) -> str:
        """
        Finalize the response and return it as a raw HTTP response string.

        :return: The complete HTTP response as a string
        """

        status_message = HttpStatus.description(self._status_code)
        response_line = f"HTTP/1.1 {self._status_code} {status_message}\r\n"
        headers = ''.join(f"{key}: {value}\r\n" for key, value in self._headers.items())
        response = response_line + headers + "\r\n" + self._body

        return response

    @staticmethod
    def _get_status_message(status_code: int) -> str:
        """
        Return a human-readable status message for a given status code.

        :param status_code: The HTTP status code
        :return: The corresponding status message
        """
        status_messages = {
            200: "OK",
            201: "Created",
            204: "No Content",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable",
        }
        return status_messages.get(status_code, "Unknown Status")

    def __repr__(self) -> str:
        return f"<Response {self._status_code} with {len(self._body)} bytes>"