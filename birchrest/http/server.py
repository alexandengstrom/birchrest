from json import JSONDecodeError
import socket
from typing import Callable, Optional, Awaitable
import asyncio

from .request import Request
from .response import Response
from ..utils import Logger


class Server:
    """
    A simple socket-based HTTP server that handles incoming client connections
    and processes HTTP requests.

    The server accepts incoming TCP connections, reads and parses HTTP requests,
    passes them to a request handler, and sends back the corresponding HTTP response.

    Attributes:
        host (str): The server's hostname or IP address. Defaults to '127.0.0.1'.
        port (int): The port the server listens on. Defaults to 5000.
        backlog (int): The maximum number of queued connections. Defaults to 5.
        server_socket (Optional[socket.socket]): The server's main socket.
        request_handler (Callable[[Request], Response]): A function that processes
            the incoming HTTP request and returns a response.
    """

    def __init__(
        self,
        request_handler: Callable[[Request], Awaitable[Response]],
        host: str = "127.0.0.1",
        port: int = 5000,
        backlog: int = 5,
    ) -> None:
        """
        Initializes the server with a request handler, host, port, and backlog size.

        :param request_handler: A callable that processes HTTP requests and returns responses.
        :param host: The hostname or IP address to bind the server to. Defaults to '127.0.0.1'.
        :param port: The port to bind the server to. Defaults to 5000.
        :param backlog: The maximum number of queued connections. Defaults to 5.
        """

        self.host: str = host
        self.port: int = port
        self.backlog: int = backlog
        self.server_socket: Optional[socket.socket] = None
        self.request_handler = request_handler
        self._server: Optional[asyncio.AbstractServer] = None

    async def start(self) -> None:
        """
        Starts the server and begins listening for incoming connections asynchronously.
        """
        self._server = await asyncio.start_server(
            self._handle_client, self.host, self.port
        )
        Logger.info(f"Running on: {self.host}:{self.port}")
        Logger.info("Press Ctrl+C to stop the server.")

        async with self._server:
            await self._server.serve_forever()

    async def _handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """
        Handles communication with a client, reading the request data, processing
        the request, and sending back the response asynchronously.
        """
        try:
            request_data = ""
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                request_data += data.decode("utf-8")
                if len(data) < 1024:
                    break

            client_address, client_port = writer.get_extra_info("peername")

            try:
                request = Request.parse(request_data, client_address, client_port)
            except JSONDecodeError:
                Logger.warning("Failed to parse request as JSON")
                response = (
                    Response()
                    .status(400)
                    .send(
                        {"error": "Failed to parse request, likely invalid JSON format"}
                    )
                    .end()
                )
                writer.write(response.encode("utf-8"))
                await writer.drain()
                return
            except Exception as e:
                response = (
                    Response().status(400).send({"error": "Malformed request"}).end()
                )
                writer.write(response.encode("utf-8"))
                await writer.drain()
                return

            res: Response = await self.request_handler(request)

            if res._is_sent:
                writer.write(res.end().encode("utf-8"))
                await writer.drain()
        except Exception as e:
            response = (
                Response().status(500).send({"error": "Internal server error"}).end()
            )
            writer.write(response.encode("utf-8"))
            await writer.drain()
        finally:
            writer.close()
            await writer.wait_closed()

    async def shutdown(self) -> None:
        """
        Gracefully shuts down the server by closing the server socket and stopping the server loop.
        """
        if self._server is not None:
            print("Shutting down the server...")
            self._server.close()
            await self._server.wait_closed()
            print("Server successfully shut down.")
        else:
            print("Server is not running.")
