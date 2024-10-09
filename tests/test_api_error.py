# type: ignore

import unittest
from unittest.mock import Mock
from birchrest.http.response import Response
from birchrest.exceptions.api_error import ApiError
from birchrest.http.status import HttpStatus


class TestApiError(unittest.TestCase):

    def test_api_error_initialization(self):
        """Test the initialization of ApiError."""
        error = ApiError("Test message", 404)
        self.assertEqual(error.user_message, "Test message")
        self.assertEqual(error.status_code, 404)
        self.assertEqual(error.base_message, HttpStatus.description(404))

    def test_api_error_str(self):
        """Test the string representation of ApiError."""
        error = ApiError("Test message", 404)
        self.assertEqual(str(error), "[404] Test message")

    def test_convert_to_response(self):
        """Test convert_to_response method for ApiError."""
        mock_response = Mock(spec=Response)
        mock_response.correlation_id = "test-correlation-id"
        mock_response.status.return_value = mock_response
        mock_response.send.return_value = mock_response

        error = ApiError("Test message", 404)
        response = error.convert_to_response(mock_response)

        expected_payload = {
            "error": {
                "status": 404,
                "code": HttpStatus.description(404),
                "correlationId": "test-correlation-id",
                "message": "Test message"
            }
        }

        mock_response.status.assert_called_with(404)
        mock_response.send.assert_called_with(expected_payload)
        self.assertEqual(response, mock_response)

    def test_convert_to_response_without_user_message(self):
        """Test convert_to_response when no user_message is provided."""
        mock_response = Mock(spec=Response)
        mock_response.correlation_id = "test-correlation-id"
        mock_response.status.return_value = mock_response
        mock_response.send.return_value = mock_response

        error = ApiError("", 404)
        response = error.convert_to_response(mock_response)

        expected_payload = {
            "error": {
                "status": 404,
                "code": HttpStatus.description(404),
                "correlationId": "test-correlation-id"
            }
        }

        mock_response.status.assert_called_with(404)
        mock_response.send.assert_called_with(expected_payload)
        self.assertEqual(response, mock_response)

    def test_bad_request(self):
        """Test BAD_REQUEST factory method."""
        error = ApiError.BAD_REQUEST("Bad request error")
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.user_message, "Bad request error")

    def test_unauthorized(self):
        """Test UNAUTHORIZED factory method."""
        error = ApiError.UNAUTHORIZED("Unauthorized error")
        self.assertEqual(error.status_code, 401)
        self.assertEqual(error.user_message, "Unauthorized error")

    def test_forbidden(self):
        """Test FORBIDDEN factory method."""
        error = ApiError.FORBIDDEN("Forbidden error")
        self.assertEqual(error.status_code, 403)
        self.assertEqual(error.user_message, "Forbidden error")

    def test_not_found(self):
        """Test NOT_FOUND factory method."""
        error = ApiError.NOT_FOUND("Not found error")
        self.assertEqual(error.status_code, 404)
        self.assertEqual(error.user_message, "Not found error")

    def test_method_not_allowed(self):
        """Test METHOD_NOT_ALLOWED factory method."""
        error = ApiError.METHOD_NOT_ALLOWED("Method not allowed error")
        self.assertEqual(error.status_code, 405)
        self.assertEqual(error.user_message, "Method not allowed error")

    def test_internal_server_error(self):
        """Test INTERNAL_SERVER_ERROR factory method."""
        error = ApiError.INTERNAL_SERVER_ERROR("Internal server error")
        self.assertEqual(error.status_code, 500)
        self.assertEqual(error.user_message, "Internal server error")


if __name__ == '__main__':
    unittest.main()
