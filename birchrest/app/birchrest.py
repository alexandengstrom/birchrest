"""
This module defines the `BirchRest` class, which is the core component of the 
BirchRest framework. The class is responsible for handling the registration of 
controllers, global middleware, authentication and error handling, as well as 
serving the API via an HTTP server. It also manages routing, request handling, 
and exception management during the lifecycle of a request.

Modules imported include:
- `exceptions`: Handles API-related errors and invalid controller registration.
- `http`: Manages the server and request/response objects.
- `routes`: Provides the base Controller and Route for registering API endpoints.
- `utils`: Utility functions like `get_artwork` for server startup.
- `version`: Holds the current version of the BirchRest framework.
"""

from typing import Awaitable, Dict, List, Optional, Type
import asyncio

from birchrest.exceptions.api_error import ApiError
from birchrest.http.server import Server
from birchrest.routes import Route, Controller
from birchrest.utils.artwork import get_artwork
from birchrest.version import __version__
from ..http import Request, Response
from ..exceptions import InvalidControllerRegistration
from ..types import MiddlewareFunction, AuthHandlerFunction, ErrorHandler


class BirchRest:
    """
    The core application class for the BirchRest framework, responsible for
    registering controllers, middleware, authentication, error handling,
    and starting the HTTP server to serve the API.

    Attributes:
        controllers (List[Controller]): Registered route controllers.
        global_middlewares (List[MiddlewareFunction]): Global middleware applied to all routes.
        auth_handler (Optional[AuthHandlerFunction]): Authentication handler for protected routes.
        error_handler (Optional[ErrorHandler]): Error handler function for handling exceptions.
    """

    def __init__(self) -> None:
        """
        Initializes the BirchRest application with empty lists of controllers,
        global middleware, and optional handlers for authentication and error handling.
        """
        self.controllers: List[Controller] = []
        self.global_middlewares: List[MiddlewareFunction] = []
        self.routes: List[Route] = []
        self.auth_handler: Optional[AuthHandlerFunction] = None
        self.error_handler: Optional[ErrorHandler] = None

    def register(self, *controllers: Type[Controller]) -> None:
        """
        Registers one or more route controllers to the application.

        Args:
            *controllers (Type[Controller]): One or more controller classes to register.

        Raises:
            InvalidControllerRegistration: If a registered controller does not inherit from `Controller`.
        """

        for controller in controllers:
            if not issubclass(controller, Controller):
                raise InvalidControllerRegistration(controller)

            self.controllers.append(controller())

    def auth(self, auth_handler: AuthHandlerFunction) -> None:
        """
        Sets the authentication handler for the application, used for protecting routes.

        Args:
            auth_handler (AuthHandlerFunction): A function to handle authentication logic.
        """

        self.auth_handler = auth_handler

    def middleware(self, handler: MiddlewareFunction) -> None:
        """
        Registers a global middleware that is applied to all routes.

        Args:
            handler (MiddlewareFunction): A middleware function to process requests.
        """

        self.global_middlewares.append(handler)

    def error(self, handler: ErrorHandler) -> None:
        """
        Registers a global error handler for the application.

        Args:
            handler (ErrorHandler): A function to handle errors during request processing.
        """

        self.error_handler = handler

    def serve(self, host: str = "127.0.0.1", port: int = 13337) -> None:
        """
        Starts the HTTP server to serve the API on the specified host and port.

        Args:
            host (str): The hostname or IP address to bind the server to. Defaults to "127.0.0.1".
            port (int): The port number to listen on. Defaults to 13337.
        """

        self._build_api()
        server = Server(self.handle_request, host=host, port=port)

        print(get_artwork(host, port, __version__))

        try:
            asyncio.run(server.start())
        except KeyboardInterrupt:
            print("\nServer shutdown initiated by user. Exiting...")
        finally:
            asyncio.run(server.shutdown())
            print("Server stopped.")

    async def handle_request(self, request: Request) -> Response:
        """
        Handles incoming HTTP requests by matching them to routes, processing middleware,
        and handling exceptions asynchronously.
        """
        response = Response(request.correlation_id)

        try:
            return await self._handle_request(request, response)
        except ApiError as e:
            if self.error_handler:
                if asyncio.iscoroutinefunction(self.error_handler):
                    await self.error_handler(request, response, e)
                else:
                    self.error_handler(request, response, e)
                return response

            return e.convert_to_response(response)
        except Exception as e:
            if self.error_handler:
                if asyncio.iscoroutinefunction(self.error_handler):
                    await self.error_handler(request, response, e)
                else:
                    self.error_handler(request, response, e)
                return response

            return response.status(500).send(
                {"error": {"status": 500, "code": "Internal Server Error"}}
            )

    async def _handle_request(self, request: Request, response: Response) -> Response:
        matched_route: Optional[Route] = None
        path_params: Optional[Dict[str, str]] = {}

        route_exists = False

        for route in self.routes:
            params = route.match(request.clean_path)

            if params is not None:
                route_exists = True

                if route.is_method_allowed(request.method):
                    matched_route = route
                    path_params = params if params is not None else {}
                    break

        if matched_route:
            if matched_route.requires_params and not path_params:
                raise ApiError.BAD_REQUEST("400 Bad Request - Missing Parameters")
            else:
                request.params = path_params if path_params is not None else {}
                await matched_route(request, response)
        else:
            if route_exists:
                raise ApiError.METHOD_NOT_ALLOWED()
            else:
                raise ApiError.NOT_FOUND()

        return response

    def _build_api(self) -> None:
        """
        Constructs the API by registering all routes from the controllers and applying
        global middleware and authentication handlers.
        """

        for controller in self.controllers:
            controller.resolve_paths(middlewares=self.global_middlewares)

        for controller in self.controllers:
            for route in controller.collect_routes():
                route.register_auth_handler(self.auth_handler)
                self.routes.append(route)
