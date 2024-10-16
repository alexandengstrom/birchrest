# type: ignore

import unittest
from unittest.mock import patch, AsyncMock, Mock
import asyncio
from birchrest.http.server import Server
from birchrest.http.request import Request
from birchrest.http.response import Response


class TestServer(unittest.IsolatedAsyncioTestCase):
    
    @patch('asyncio.start_server', new_callable=AsyncMock)
    async def test_server_start(self, mock_start_server):
        """Test that the server starts and binds to the correct host and port."""

        async def mock_request_handler(request: Request) -> Response:
            return Response().status(200).send({"message": "OK"})

        server = Server(request_handler=mock_request_handler, host="127.0.0.1", port=8000)

        await server.start()

        mock_start_server.assert_called_once_with(server._handle_client, "127.0.0.1", 8000)

if __name__ == "__main__":
    unittest.main()
