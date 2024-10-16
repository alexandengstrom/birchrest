# type: ignore

import unittest
from unittest.mock import Mock, patch, mock_open, MagicMock
from birchrest import BirchRest
from birchrest.exceptions import InvalidControllerRegistration, ApiError, NotFound
from birchrest.routes import Controller
from birchrest.http import Request, Response, HttpStatus
from birchrest.types import MiddlewareFunction, AuthHandlerFunction, ErrorHandler
import json
import asyncio
import os


class MockController(Controller):
    """A mock controller for testing purposes."""
    def resolve_paths(self, prefix="", middlewares=None):
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

        with patch.object(self.birch_rest, '_handle_request', return_value=mock_response):
            response = await self.birch_rest.handle_request(mock_request)
            self.assertEqual(response, mock_response)

    @patch('birchrest.http.Request')
    async def test_handle_request_api_error(self, MockRequest):
        """Test handling an API error."""
        mock_request = MockRequest()
        mock_request.correlation_id = 'test-correlation-id'

        with patch.object(self.birch_rest, '_handle_request', side_effect=NotFound):
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

        mock_controller.resolve_paths.assert_called_once_with(prefix="", middlewares=self.birch_rest.global_middlewares)
        mock_controller.collect_routes.assert_called_once()

    def test_build_api_with_auth_handler(self):
        """Test that routes receive an auth handler if it's registered."""
        mock_controller = MockController()
        self.birch_rest.controllers = [mock_controller]

        mock_auth_handler = Mock(spec=AuthHandlerFunction)
        self.birch_rest.auth(mock_auth_handler)

        mock_route = Mock()
        mock_controller.collect_routes = Mock(return_value=[mock_route])

        mock_controller.resolve_paths = Mock(side_effect=lambda prefix="", middlewares=None: None)

        self.birch_rest._build_api()

        mock_route.register_auth_handler.assert_called_with(mock_auth_handler)

    @patch('os.walk', return_value=[('/some/path', ['subdir'], ['__birch__.py'])])
    @patch('birchrest.BirchRest._import_birch_file')
    def test_discover_controllers(self, mock_import_birch_file, mock_os_walk):
        """Test _discover_controllers to ensure it discovers the __birch__.py file and imports it."""
        self.birch_rest._discover_controllers()
        mock_import_birch_file.assert_called_once_with('/some/path/__birch__.py')

    @patch('importlib.util.spec_from_file_location')
    @patch('importlib.util.module_from_spec')
    def test_import_birch_file_with_openapi(self, mock_module_from_spec, mock_spec_from_file_location):
        """Test _import_birch_file to ensure OpenAPI is loaded if present."""
        mock_module = MagicMock()
        mock_module.__openapi__ = {'info': 'test'}
        mock_module_from_spec.return_value = mock_module

        spec_mock = MagicMock()
        mock_spec_from_file_location.return_value = spec_mock

        self.birch_rest._import_birch_file('/some/path/__birch__.py')

        self.assertEqual(self.birch_rest.openapi, {'info': 'test'})

    @patch('birchrest.utils.Logger.warning')
    @patch('importlib.util.spec_from_file_location')
    @patch('importlib.util.module_from_spec')
    def test_import_birch_file_without_openapi(self, mock_module_from_spec, mock_spec_from_file_location, mock_logger_warning):
        """Test _import_birch_file to ensure OpenAPI is skipped if not present."""
        mock_module = MagicMock()
        del mock_module.__openapi__
        mock_module_from_spec.return_value = mock_module

        spec_mock = MagicMock()
        mock_spec_from_file_location.return_value = spec_mock

        self.birch_rest._import_birch_file('/some/path/__birch__.py')

        mock_logger_warning.assert_called_once_with('No __openapi__ variable found in /some/path/__birch__.py')

    @patch('traceback.format_tb', return_value=['trace'])
    @patch('birchrest.utils.Logger.error')
    def test_warn_about_unhandled_exception(self, mock_logger_error, mock_format_tb):
        """Test _warn_about_unhandled_exception to ensure unhandled exceptions are logged."""
        exception = Exception('Test Exception')
        self.birch_rest._warn_about_unhandled_exception(exception)

        mock_logger_error.assert_called_once_with(
            "Unhandled Exception! Status code 500 was sent to the user",
            {
                "Exception Type": "Exception",
                "Exception Message": "Test Exception",
                "Traceback": "trace",
            },
        )

if __name__ == '__main__':
    unittest.main()
