from typing import Any, Dict, Optional

from birchrest.http.request import Request
from birchrest.http.response import Response
from ..app.birchrest import BirchRest
import json

class TestAdapter:
    def __init__(self, app: BirchRest) -> None:
        self.app = app

    def get(self, path: str, headers: Dict[str, str] = {}, body: Optional[Any] = None) -> Response:
        """Simulate a GET request."""
        request = self._generate_request("GET", path, headers, body)
        return self.app.handle_request(request)

    def post(self, path: str, headers: Dict[str, str] = {}, body: Optional[Any] = None) -> Response:
        """Simulate a POST request."""
        request = self._generate_request("POST", path, headers, body)
        return self.app.handle_request(request)

    def put(self, path: str, headers: Dict[str, str] = {}, body: Optional[Any] = None) -> Response:
        """Simulate a PUT request."""
        request = self._generate_request("PUT", path, headers, body)
        return self.app.handle_request(request)

    def patch(self, path: str, headers: Dict[str, str] = {}, body: Optional[Any] = None) -> Response:
        """Simulate a PATCH request."""
        request = self._generate_request("PATCH", path, headers, body)
        return self.app.handle_request(request)

    def delete(self, path: str, headers: Dict[str, str] = {}, body: Optional[Any] = None) -> Response:
        """Simulate a DELETE request."""
        request = self._generate_request("DELETE", path, headers, body)
        return self.app.handle_request(request)

    def head(self, path: str, headers: Dict[str, str] = {}) -> Response:
        """Simulate a HEAD request."""
        request = self._generate_request("HEAD", path, headers)
        return self.app.handle_request(request)

    def options(self, path: str, headers: Dict[str, str] = {}) -> Response:
        """Simulate an OPTIONS request."""
        request = self._generate_request("OPTIONS", path, headers)
        return self.app.handle_request(request)

    def _generate_request(self, method: str, path: str, headers: Dict[str, str] = {}, body: Optional[Any] = None) -> Request:
        """Helper method to generate a request object for testing."""

        request = Request(
            method,
            path,
            "HTTP/1.1",
            headers,
            json.dumps(body),
            "testadapter-agent"
        )
        return request

