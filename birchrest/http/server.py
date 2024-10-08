from json import JSONDecodeError
import socket
from threading import Thread
from typing import Callable, Optional, Any

from .request import Request
from .response import Response


class Server:
    def __init__(
        self,
        request_handler: Callable,
        host: str = "127.0.0.1",
        port: int = 5000,
        backlog: int = 5
    ) -> None:

        self.host: str = host
        self.port: int = port
        self.backlog: int = backlog
        self.server_socket: Optional[socket.socket] = None
        self.request_handler = request_handler

    def start(self) -> None:
        """
        Start the socket server.
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.backlog)
        print(f"Server started at {self.host}:{self.port}")

        self._accept_connections()

    def _accept_connections(self) -> None:
        """
        Accept incoming connections and handle them in separate threads.
        """
        assert self.server_socket

        while True:
            client_socket, client_address = self.server_socket.accept()

            client_thread = Thread(
                target=self._handle_client,
                args=(client_socket, client_address[0])
            )

            client_thread.start()

    def _handle_client(self, client_socket: socket.socket, client_address: str) -> None:
        """
        Handle communication with a client, reading the entire request data
        by looping until all data is received.
        """
        try:
            request_data = ""
            while True:
                chunk = client_socket.recv(1024).decode('utf-8')
                request_data += chunk

                if len(chunk) < 1024:
                    break
            
            request = None
            
            try:
                request = Request.parse(request_data, client_address)
            except JSONDecodeError:
                client_socket.sendall(Response().status(400).send(
                {"error": "Failed to parse request, likely invalid JSON format"}).end().encode('utf-8')
            )
                return
            except:
                client_socket.sendall(Response().status(400).send(
                {"error": "Malformed request"}).end().encode('utf-8')
            )
                return
                
            response = self.request_handler(request)

            client_socket.sendall(response.end().encode('utf-8'))
        except Exception as e:
            print(e.with_traceback())
            client_socket.sendall(Response().status(500).send(
                {"error": "Internal server error"}).end().encode('utf-8')
            )
        finally:
            client_socket.close()

    def shutdown(self) -> None:
        """
        Shut down the server gracefully.
        """
        if self.server_socket:
            self.server_socket.close()
            print("Server shutdown.")