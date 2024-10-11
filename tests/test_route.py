# type: ignore

import unittest
from dataclasses import dataclass, field
from unittest.mock import Mock, patch, AsyncMock
from birchrest.routes.route import Route
from birchrest.http import Request, Response
from birchrest.exceptions.api_error import ApiError
from birchrest.exceptions import MissingAuthHandlerError
from birchrest.routes.validator import parse_data_class

@dataclass
class Address:
    street: str = field(metadata={"min_length": 3, "max_length": 100})
    city: str = field(metadata={"min_length": 2, "max_length": 50})

@dataclass
class User:
    username: str = field(metadata={"min_length": 3, "max_length": 20})
    email: str = field(metadata={"regex": r"^[\w\.-]+@[\w\.-]+\.\w+$"})
    age: int = field(metadata={"min_value": 0, "max_value": 120})
    address: Address

class TestRoute(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        """Set up mocks for the tests."""
        self.mock_func = AsyncMock()
        self.mock_request = Mock(spec=Request)
        self.mock_response = Mock(spec=Response)
        self.mock_auth_handler = AsyncMock()
        self.middlewares = [AsyncMock()]

    def test_initialization(self):
        """Test that Route initializes correctly."""
        route = Route(self.mock_func, "GET", "/test", self.middlewares, False, None, None, None)

        self.assertEqual(route.func, self.mock_func)
        self.assertEqual(route.method, "GET")
        self.assertEqual(route.path, "/test")
        self.assertEqual(route.middlewares, self.middlewares)
        self.assertFalse(route.is_protected)
        self.assertIsNone(route.validate_body)
        self.assertIsNone(route.validate_queries)
        self.assertIsNone(route.validate_params)

    def test_resolve(self):
        """Test that resolve properly updates path and middlewares."""
        route = Route(self.mock_func, "GET", "/test/:id", self.middlewares, False, None, None, None)
        route.resolve("/api", ["global_middleware"])

        self.assertEqual(route.path, "/api/test/:id")
        self.assertEqual(route.middlewares, ["global_middleware"] + self.middlewares)
        self.assertEqual(route.param_names, ["id"])
        self.assertTrue(route.requires_params)
        self.assertIsNotNone(route.regex)
        
    async def test_call_route_with_middlewares(self):
        """Test that the route runs middlewares and calls the handler."""
        async def sample_middleware(req, res, next_func):
            await next_func()

        self.middlewares = [AsyncMock(side_effect=sample_middleware)]
        route = Route(self.mock_func, "GET", "/test", self.middlewares, False, None, None, None)
        await route(self.mock_request, self.mock_response)
        self.middlewares[0].assert_called_once()
        self.mock_func.assert_called_once_with(self.mock_request, self.mock_response)

    async def test_call_route_with_protection_and_auth(self):
        """Test that the route checks authentication for protected routes."""
        
        async def sample_middleware(req, res, next_func):
            await next_func()

        self.middlewares = [AsyncMock(side_effect=sample_middleware)]

        route = Route(self.mock_func, "GET", "/test", self.middlewares, True, None, None, None)
        route.register_auth_handler(self.mock_auth_handler)
        self.mock_auth_handler.return_value = {"user_id": 1}

        await route(self.mock_request, self.mock_response)

        self.mock_auth_handler.assert_called_once_with(self.mock_request, self.mock_response)
        self.assertEqual(self.mock_request.user, {"user_id": 1})
        self.mock_func.assert_called_once_with(self.mock_request, self.mock_response)
        
    async def test_call_route_with_validation(self):
        """Test that body, queries, and params are validated using dataclasses."""
        
        async def sample_middleware(req, res, next_func):
            await next_func()

        self.middlewares = [AsyncMock(side_effect=sample_middleware)]

        route = Route(self.mock_func, "POST", "/test", self.middlewares, False, User, None, None)

        self.mock_request.body = {
            "username": "testuser",
            "email": "test@example.com",
            "age": 30,
            "address": {
                "street": "123 Main St",
                "city": "New York"
            }
        }

        with patch("birchrest.routes.route.parse_data_class") as mock_parse:
            mock_parse.side_effect = [
                {"username": "testuser", "email": "test@example.com", "age": 30, "address": {"street": "123 Main St", "city": "New York"}}
            ]

            await route(self.mock_request, self.mock_response)

            mock_parse.assert_any_call(User, self.mock_request.body)

            self.mock_func.assert_called_once_with(self.mock_request, self.mock_response)


    async def test_call_route_without_auth_handler_raises_error(self):
        """Test that a MissingAuthHandlerError is raised when no auth handler is registered."""
        route = Route(self.mock_func, "GET", "/test", self.middlewares, True, None, None, None)

        with self.assertRaises(MissingAuthHandlerError):
            await route(self.mock_request, self.mock_response)

    def test_match(self):
        """Test that match correctly matches paths and extracts parameters."""
        route = Route(self.mock_func, "GET", "/test/:id", self.middlewares, False, None, None, None)
        route.resolve("/api", [])

        match = route.match("/api/test/123")
        self.assertEqual(match, {"id": "123"})

        no_match = route.match("/api/invalid/123")
        self.assertIsNone(no_match)
        
    def test_complex_match(self):
        """Test that match correctly handles more complex paths with multiple parameters."""

        route = Route(self.mock_func, "GET", "/users/:user_id/orders/:order_id", self.middlewares, False, None, None, None)
        route.resolve("/api/v1", [])

        match = route.match("/api/v1/users/42/orders/123")
        self.assertEqual(match, {"user_id": "42", "order_id": "123"})

        no_match = route.match("/api/v1/users/42/products/123")
        self.assertIsNone(no_match)
        
    def test_complex_match_with_special_characters(self):
        """Test that match correctly handles special characters and slashes in paths."""
        route = Route(self.mock_func, "GET", "/users/:email/items/:item_id", self.middlewares, False, None, None, None)
        route.resolve("/api/v1", [])

        match = route.match("/api/v1/users/test.user@example.com/items/987")
        self.assertEqual(match, {"email": "test.user@example.com", "item_id": "987"})

        no_match = route.match("/api/v1/users/test.user@example.com/orders/987")
        self.assertIsNone(no_match)

    def test_is_method_allowed(self):
        """Test that is_method_allowed checks the correct HTTP method."""
        route = Route(self.mock_func, "GET", "/test", self.middlewares, False, None, None, None)

        self.assertTrue(route.is_method_allowed("GET"))
        self.assertFalse(route.is_method_allowed("POST"))

    def test_auth_handler_protected_route(self):
        """Test that make_protected and auth_handler work together."""
        route = Route(self.mock_func, "GET", "/test", self.middlewares, False, None, None, None)
        route.make_protected()
        route.register_auth_handler(self.mock_auth_handler)

        self.assertTrue(route.is_protected)
        self.assertEqual(route.auth_handler, self.mock_auth_handler)


if __name__ == "__main__":
    unittest.main()
