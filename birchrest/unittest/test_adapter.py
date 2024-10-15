from typing import Any, Dict, Optional
import json
from birchrest.http.request import Request
from birchrest.http.response import Response
from ..app.birchrest_app import BirchRest


class TestAdapter:
    """
    A test wrapper for simulating HTTP requests in a BirchRest application.

    The `TestAdapter` class provides a convenient way to simulate HTTP requests such as
    GET, POST, PUT, PATCH, DELETE, HEAD, and OPTIONS during testing. It interacts directly
    with the BirchRest application instance and can be used to test routes and endpoints
    without requiring a live server.

    This class generates `Request` objects with the appropriate HTTP method, headers,
    and body, and passes them to the application for processing. The responses returned
    by the application can then be validated in tests.

    Attributes:
        app (BirchRest): The instance of the BirchRest application being tested.

    Methods:
        get(path, headers, body): Simulates a GET request to the application.
        post(path, headers, body): Simulates a POST request to the application.
        put(path, headers, body): Simulates a PUT request to the application.
        patch(path, headers, body): Simulates a PATCH request to the application.
        delete(path, headers, body): Simulates a DELETE request to the application.
        head(path, headers): Simulates a HEAD request to the application.
        options(path, headers): Simulates an OPTIONS request to the application.
        _generate_request(method, path, headers, body): Helper method to create a `Request` object.
    """

    def __init__(self, app: BirchRest) -> None:
        self.app = app
        self.app._build_api()

    async def get(
        self, path: str, headers: Dict[str, str] = {}, body: Optional[Any] = None
    ) -> Response:
        """Simulate a GET request."""
        request = self._generate_request("GET", path, headers, body)
        return await self.app.handle_request(request)

    async def post(
        self, path: str, headers: Dict[str, str] = {}, body: Optional[Any] = None
    ) -> Response:
        """Simulate a POST request."""
        request = self._generate_request("POST", path, headers, body)
        return await self.app.handle_request(request)

    async def put(
        self, path: str, headers: Dict[str, str] = {}, body: Optional[Any] = None
    ) -> Response:
        """Simulate a PUT request."""
        request = self._generate_request("PUT", path, headers, body)
        return await self.app.handle_request(request)

    async def patch(
        self, path: str, headers: Dict[str, str] = {}, body: Optional[Any] = None
    ) -> Response:
        """Simulate a PATCH request."""
        request = self._generate_request("PATCH", path, headers, body)
        return await self.app.handle_request(request)

    async def delete(
        self, path: str, headers: Dict[str, str] = {}, body: Optional[Any] = None
    ) -> Response:
        """Simulate a DELETE request."""
        request = self._generate_request("DELETE", path, headers, body)
        return await self.app.handle_request(request)

    async def head(self, path: str, headers: Dict[str, str] = {}) -> Response:
        """Simulate a HEAD request."""
        request = self._generate_request("HEAD", path, headers)
        return await self.app.handle_request(request)

    async def options(self, path: str, headers: Dict[str, str] = {}) -> Response:
        """Simulate an OPTIONS request."""
        request = self._generate_request("OPTIONS", path, headers)
        return await self.app.handle_request(request)

    def _generate_request(
        self,
        method: str,
        path: str,
        headers: Dict[str, str] = {},
        body: Optional[Any] = None,
    ) -> Request:
        """Helper method to generate a request object for testing."""

        request = Request(
            method, path, "HTTP/1.1", headers, json.dumps(body), "testadapter-agent"
        )
        return request
