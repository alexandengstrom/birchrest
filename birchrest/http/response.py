import json
from typing import Dict, Any
from .status import HttpStatus


class Response:
    """
    Represents an HTTP response, providing methods to set status codes, headers,
    and the response body. It also supports sending JSON-encoded data and
    generating the final raw HTTP response as a string.

    Attributes:
        _status_code (int): The HTTP status code of the response.
        _headers (Dict[str, str]): A dictionary containing the response headers.
        _body (str): The response body.
        _is_sent (bool): A flag to indicate if the response has already been sent.
        correlation_id (str): A unique correlation ID for tracking the request-response cycle.
    """

    def __init__(self, correlation_id: str = "") -> None:
        """
        Initializes a new Response object with default values.
        """
        self._status_code: int = 200
        self._headers: Dict[str, str] = {"Content-Type": "text/html"}
        self._body: str = ""
        self._is_sent: bool = False
        self.correlation_id = correlation_id
        self.body: Any
        self.json: str

    def status(self, code: int) -> "Response":
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

    def set_header(self, name: str, value: str) -> "Response":
        """
        Set an HTTP header.

        :param name: The name of the header
        :param value: The value of the header
        :return: self to allow chaining
        """
        self._headers[name] = value
        return self

    def send(self, data: Any = {}) -> "Response":
        """
        Set the response body to a JSON-encoded string and set
        Content-Type to application/json.

        :param data: A dictionary to be JSON-encoded
        :return: self to allow for chaining
        """

        if self._is_sent:
            raise RuntimeError(
                "You tried to send the response twice, make sure you only send the response once."
            )

        self.body = data
        self.json = json.dumps(data)
        self._body = json.dumps(data)
        self.set_header("Content-Type", "application/json")
        self._headers["Content-Length"] = str(len(self._body))
        self._is_sent = True
        return self

    def end(self) -> str:
        """
        Finalize the response and return it as a raw HTTP response string.

        :return: The complete HTTP response as a string
        """

        status_message = HttpStatus.description(self._status_code)
        response_line = f"HTTP/1.1 {self._status_code} {status_message}\r\n"
        headers = "".join(f"{key}: {value}\r\n" for key, value in self._headers.items())
        response = response_line + headers + "\r\n" + self.json

        return response

    def __repr__(self) -> str:
        return f"<Response {self._status_code} with {len(self._body)} bytes>"
