from json import JSONDecodeError
import socket
from threading import Thread
from typing import Callable, Optional, Any

from .request import Request
from .response import Response
from ..types import RouteHandler


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
        request_handler: Callable[[Request], Response],
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

    def start(self) -> None:
        """
        Starts the server and begins listening for incoming connections.
        Sets up the server socket, binds it to the configured host and port, and begins
        accepting connections.

        :raises OSError: If the server cannot bind to the specified host or port.
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.backlog)
        print(f"\033[92mRunning on: {self.host}:{self.port}\033[0m")
        print("\033[93mPress Ctrl+C to stop the server.\033[0m")

        self._accept_connections()

    def _accept_connections(self) -> None:
        """
        Accepts incoming client connections and handles them in separate threads.

        This method continuously waits for new connections on the server socket and 
        spawns a new thread to handle each client connection.
        """
        assert self.server_socket

        while True:
            client_socket, client_address = self.server_socket.accept()

            client_thread = Thread(
                target=self._handle_client, args=(client_socket, client_address[0])
            )

            client_thread.start()

    def _handle_client(self, client_socket: socket.socket, client_address: str) -> None:
        """
        Handles the communication with a client, reading the request data, processing
        the request, and sending back the response.

        Reads the client's request data in chunks, parses it into a Request object,
        and uses the request handler to generate a Response. The response is then
        sent back to the client.

        :param client_socket: The socket object representing the client connection.
        :param client_address: The IP address of the connected client.
        """
        try:
            request_data = ""
            while True:
                chunk = client_socket.recv(1024).decode("utf-8")
                request_data += chunk

                if len(chunk) < 1024:
                    break

            request = None

            try:
                request = Request.parse(request_data, client_address)
            except JSONDecodeError:
                client_socket.sendall(
                    Response()
                    .status(400)
                    .send(
                        {"error": "Failed to parse request, likely invalid JSON format"}
                    )
                    .end()
                    .encode("utf-8")
                )
                return
            except Exception as e:
                client_socket.sendall(
                    Response()
                    .status(400)
                    .send({"error": "Malformed request"})
                    .end()
                    .encode("utf-8")
                )
                return

            response = self.request_handler(request)

            if response._is_sent:
                client_socket.sendall(response.end().encode("utf-8"))
        except Exception as e:
            print(e)
            client_socket.sendall(
                Response()
                .status(500)
                .send({"error": "Internal server error"})
                .end()
                .encode("utf-8")
            )
        finally:
            client_socket.close()

    def shutdown(self) -> None:
        """
        Shuts down the server by closing the server socket.

        This method should be called when you want to stop the server gracefully.
        """
        if self.server_socket:
            self.server_socket.close()

