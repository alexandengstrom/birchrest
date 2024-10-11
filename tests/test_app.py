# type: ignore

import unittest
from unittest.mock import Mock, patch
from birchrest import BirchRest
from birchrest.exceptions import InvalidControllerRegistration, ApiError
from birchrest.routes import Controller
from birchrest.http import Request, Response, HttpStatus
from birchrest.types import MiddlewareFunction, AuthHandlerFunction, ErrorHandler
import json


class MockController(Controller):
    """A mock controller for testing purposes."""
    def resolve_paths(self, middlewares=None):
        pass

    def collect_routes(self):
        return []


class TestBirchRest(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        """Setup the BirchRest instance before each test."""
        self.birch_rest = BirchRest()

    def test_register_valid_controller(self):
        """Test that valid controllers are registered successfully."""
        self.birch_rest.register(MockController)
        self.assertEqual(len(self.birch_rest.controllers), 1)
        self.assertIsInstance(self.birch_rest.controllers[0], MockController)

    def test_register_invalid_controller(self):
        """Test that registering an invalid controller raises an error."""
        with self.assertRaises(InvalidControllerRegistration):
            self.birch_rest.register(object)

    def test_auth_handler(self):
        """Test setting an authentication handler."""
        mock_auth_handler = Mock(spec=AuthHandlerFunction)
        self.birch_rest.auth(mock_auth_handler)
        self.assertEqual(self.birch_rest.auth_handler, mock_auth_handler)

    def test_middleware(self):
        """Test registering a global middleware."""
        mock_middleware = Mock(spec=MiddlewareFunction)
        self.birch_rest.middleware(mock_middleware)
        self.assertEqual(len(self.birch_rest.global_middlewares), 1)
        self.assertEqual(self.birch_rest.global_middlewares[0], mock_middleware)

    def test_error_handler(self):
        """Test registering an error handler."""
        mock_error_handler = Mock(spec=ErrorHandler)
        self.birch_rest.error(mock_error_handler)
        self.assertEqual(self.birch_rest.error_handler, mock_error_handler)

    @patch('birchrest.http.Request')
    @patch('birchrest.http.Response')
    async def test_handle_request_valid(self, MockResponse, MockRequest):
        """Test handling a valid request."""
        mock_request = MockRequest()
        mock_response = MockResponse()

        # Mock the internal _handle_request method to return the response directly
        with patch.object(self.birch_rest, '_handle_request', return_value=mock_response):
            response = await self.birch_rest.handle_request(mock_request)
            self.assertEqual(response, mock_response)

    @patch('birchrest.http.Request')
    async def test_handle_request_api_error(self, MockRequest):
        """Test handling an API error."""
        mock_request = MockRequest()
        mock_request.correlation_id = 'test-correlation-id'

        with patch.object(self.birch_rest, '_handle_request', side_effect=ApiError.NOT_FOUND()):
            response = await self.birch_rest.handle_request(mock_request)


            expected_payload = {
                "error": {
                    "status": 404,
                    "code": "Not Found",
                    "correlationId": "test-correlation-id"
                }
            }

            self.assertEqual(response.body["error"]["status"], 404)
            self.assertEqual(response.body["error"]["code"], "Not Found")
            


    @patch('birchrest.http.Request')
    async def test_handle_request_internal_error(self, MockRequest):
        """Test handling an internal server error."""
        mock_request = MockRequest()


        with patch.object(self.birch_rest, '_handle_request', side_effect=Exception("Unexpected error")):
            response = await self.birch_rest.handle_request(mock_request)
            self.assertEqual(response.body["error"]["status"], 500)
            self.assertEqual(response.body["error"]["code"], "Internal Server Error")

    def test_build_api(self):
        """Test that _build_api properly resolves routes."""
        mock_controller = MockController()
        self.birch_rest.controllers = [mock_controller]

        mock_controller.resolve_paths = Mock()
        mock_controller.collect_routes = Mock(return_value=[])

        self.birch_rest._build_api()

        mock_controller.resolve_paths.assert_called_once_with(middlewares=self.birch_rest.global_middlewares)
        mock_controller.collect_routes.assert_called_once()

    def test_build_api_with_auth_handler(self):
        """Test that routes receive an auth handler if it's registered."""
        mock_controller = MockController()
        self.birch_rest.controllers = [mock_controller]

        mock_auth_handler = Mock(spec=AuthHandlerFunction)
        self.birch_rest.auth(mock_auth_handler)

        mock_route = Mock()
        mock_controller.collect_routes = Mock(return_value=[mock_route])

        self.birch_rest._build_api()

        mock_route.register_auth_handler.assert_called_with(mock_auth_handler)

if __name__ == '__main__':
    unittest.main()
