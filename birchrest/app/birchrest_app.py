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

import traceback
import os
import importlib.util
import sys
import asyncio

from typing import Dict, List, Optional, Type, Any
from colorama import init

from birchrest.exceptions.api_error import (
    ApiError,
    MethodNotAllowed,
    BadRequest,
    NotFound,
)
from birchrest.http.server import Server
from birchrest.utils import Logger
from birchrest.routes import Route, Controller
from birchrest.utils.artwork import get_artwork
from birchrest.version import __version__
from birchrest.openapi import routes_to_openapi
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

    def __init__(self, log_level: str = "debug", base_path: str = "") -> None:
        """
        Initializes the BirchRest application with empty lists of controllers,
        global middleware, and optional handlers for authentication and error handling.
        """
        self.openapi: Dict[str, Any] = {}
        self.base_path = base_path
        self.controllers: List[Controller] = []
        self.global_middlewares: List[MiddlewareFunction] = []
        self.routes: List[Route] = []
        self.auth_handler: Optional[AuthHandlerFunction] = None
        self.error_handler: Optional[ErrorHandler] = None
        self._discover_controllers()
        if os.getenv("birchrest_log_level", "").lower() != "test":
            os.environ["birchrest_log_level"] = log_level

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
            Logger.info("\nServer shutdown initiated by user. Exiting...")
        finally:
            asyncio.run(server.shutdown())
            Logger.info("Server stopped.")

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
            response._is_sent = False
            if self.error_handler:
                await self.error_handler(request, response, e)
                return response

            self._warn_about_unhandled_exception(e)

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
                raise BadRequest("400 Bad Request - Missing Parameters")

            request.params = path_params if path_params is not None else {}
            await matched_route(request, response)
        else:
            if route_exists:
                raise MethodNotAllowed

            raise NotFound

        return response

    def _build_api(self) -> None:
        """
        Constructs the API by registering all routes from the controllers and applying
        global middleware and authentication handlers.
        """

        self.controllers.append(Controller())

        for controller in self.controllers:
            controller.resolve_paths(
                prefix=self.base_path, middlewares=self.global_middlewares
            )

        for controller in self.controllers:
            for route in controller.collect_routes():
                route.register_auth_handler(self.auth_handler)
                self.routes.append(route)

    def _warn_about_unhandled_exception(self, e: Exception) -> None:
        init(autoreset=True)
        Logger.error(
            "Unhandled Exception! Status code 500 was sent to the user",
            {
                "Exception Type": type(e).__name__,
                "Exception Message": str(e),
                "Traceback": "".join(traceback.format_tb(e.__traceback__)),
            },
        )

    def _discover_controllers(self) -> None:
        """
        Searches for the __birch__.py file starting from the current working directory and imports it,
        including all controllers and other imports from that file.
        """

        current_dir = os.getcwd()

        birch_files = []
        for root, dirs, files in os.walk(current_dir):

            dirs[:] = [d for d in dirs if not d.startswith("__")]

            if "__birch__.py" in files:
                birch_files.append(os.path.join(root, "__birch__.py"))

        if not birch_files:
            raise FileNotFoundError(
                "No __birch__.py file found in the current directory or subdirectories."
            )

        for birch_file in birch_files:
            self._import_birch_file(birch_file)

    def _import_birch_file(self, birch_file: str) -> None:
        """
        Imports a given __birch__.py file.

        Args:
            birch_file (str): The path to the __birch__.py file.
        """

        module_name = os.path.splitext(os.path.basename(birch_file))[0]
        spec = importlib.util.spec_from_file_location(module_name, birch_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load the module from {birch_file}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        Logger.debug(f"Imported: {module_name} from {birch_file}")

        if hasattr(module, "__openapi__"):
            self.openapi = getattr(module, "__openapi__")
            Logger.debug(
                f"__openapi__ variable loaded and assigned to self.openapi from {birch_file}"
            )
        else:
            Logger.warning(f"No __openapi__ variable found in {birch_file}")

    def _generate_open_api(self) -> Dict[str, Any]:
        """
        Generates the full OpenAPI specification by merging the metadata from self.openapi with the paths
        generated from the registered routes.

        Returns:
            Dict[str, Any]: A dictionary representing the complete OpenAPI specification.
        """
        self._build_api()

        paths, models = routes_to_openapi(self.routes)

        openapi_spec = {
            "openapi": "3.0.0",
            **self.openapi,
            "paths": paths,
            "components": {"schemas": models},
        }

        return openapi_spec
