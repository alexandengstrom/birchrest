# type: ignore

import unittest
from unittest.mock import Mock, AsyncMock
from birchrest.middlewares import Cors
from birchrest.http import Request, Response
from birchrest.types import NextFunction


class TestCors(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        """Set up the CORS middleware instance before each test."""
        self.cors = Cors(allow_origins=["http://example.com"], allow_methods=["GET", "POST"], allow_credentials=True)

    async def test_cors_headers_added_to_non_options_request(self):
        """Test that CORS headers are added to non-OPTIONS requests."""
        mock_request = Mock(spec=Request)
        mock_request.method = "GET"
        mock_request.get_header.return_value = "http://example.com"

        mock_response = Mock(spec=Response)
        mock_next = AsyncMock(spec=NextFunction)

        await self.cors(mock_request, mock_response, mock_next)

        mock_response.set_header.assert_any_call("Access-Control-Allow-Origin", "http://example.com")
        mock_response.set_header.assert_any_call("Access-Control-Allow-Credentials", "true")

        mock_next.assert_called_once()

    async def test_preflight_request(self):
        """Test that the preflight (OPTIONS) request is handled properly."""
        mock_request = Mock(spec=Request)
        mock_request.method = "OPTIONS"
        mock_request.get_header.return_value = "http://example.com"

        mock_response = Mock(spec=Response)
        mock_response.status.return_value = mock_response
        mock_response.send.return_value = mock_response

        await self.cors(mock_request, mock_response, AsyncMock())

        mock_response.set_header.assert_any_call("Access-Control-Allow-Origin", "http://example.com")
        mock_response.set_header.assert_any_call("Access-Control-Allow-Methods", "GET, POST")
        mock_response.set_header.assert_any_call("Access-Control-Allow-Headers", "Content-Type, Authorization")
        mock_response.set_header.assert_any_call("Access-Control-Max-Age", "86400")

        mock_response.status.assert_called_with(204)
        mock_response.send.assert_called_once()

    async def test_origin_not_allowed(self):
        """Test that CORS headers are set to * when the origin is not allowed."""
        mock_request = Mock(spec=Request)
        mock_request.method = "GET"
        mock_request.get_header.return_value = "http://notallowed.com"

        mock_response = Mock(spec=Response)
        mock_next = AsyncMock(spec=NextFunction)

        await self.cors(mock_request, mock_response, mock_next)

        mock_response.set_header.assert_any_call("Access-Control-Allow-Origin", "*")

        mock_next.assert_called_once()

    async def test_credentials_not_allowed(self):
        """Test that Access-Control-Allow-Credentials is not set if credentials are not allowed."""
        cors_no_credentials = Cors(allow_origins=["http://example.com"], allow_credentials=False)
        mock_request = Mock(spec=Request)
        mock_request.method = "GET"
        mock_request.get_header.return_value = "http://example.com"

        mock_response = Mock(spec=Response)
        mock_next = AsyncMock(spec=NextFunction)

        await cors_no_credentials(mock_request, mock_response, mock_next)

        mock_response.set_header.assert_any_call("Access-Control-Allow-Origin", "http://example.com")

        credentials_header_call = ("Access-Control-Allow-Credentials", "true")
        self.assertNotIn(credentials_header_call, mock_response.set_header.call_args_list)

        mock_next.assert_called_once()


    async def test_preflight_request_with_credentials(self):
        """Test that the preflight request with credentials allowed sets the correct headers."""
        cors_with_credentials = Cors(
            allow_origins=["http://example.com"],
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type", "Authorization"],
            allow_credentials=True
        )
        mock_request = Mock(spec=Request)
        mock_request.method = "OPTIONS"
        mock_request.get_header.return_value = "http://example.com"

        mock_response = Mock(spec=Response)
        mock_response.status.return_value = mock_response
        mock_response.send.return_value = mock_response

        await cors_with_credentials(mock_request, mock_response, AsyncMock())

        mock_response.set_header.assert_any_call("Access-Control-Allow-Origin", "http://example.com")
        mock_response.set_header.assert_any_call("Access-Control-Allow-Credentials", "true")

        mock_response.set_header.assert_any_call("Access-Control-Allow-Methods", "GET, POST")
        mock_response.set_header.assert_any_call("Access-Control-Allow-Headers", "Content-Type, Authorization")
        mock_response.set_header.assert_any_call("Access-Control-Max-Age", "86400")

        mock_response.status.assert_called_with(204)
        mock_response.send.assert_called_once()



if __name__ == '__main__':
    unittest.main()
