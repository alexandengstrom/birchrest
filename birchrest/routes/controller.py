from __future__ import annotations
from typing import Generator, List
from .route import Route
from ..types import MiddlewareFunction
from ..utils import Logger


class Controller:
    """
    Base class for defining a collection of routes and subcontrollers for an HTTP API.

    The `Controller` class allows organizing routes and middleware in a structured
    manner. It collects routes defined on its methods, handles subcontrollers, and
    resolves the base path for each route. Each method decorated with HTTP method
    decorators (like GET, POST, etc.) is treated as a route, and the controller
    can apply middleware or mark routes as protected.

    Attributes:
        _base_path (str): The base path that is prefixed to all routes in this controller.
        _middlewares (List[MiddlewareFunction]): The list of middleware applied to this controller.
        _is_protected (str): Indicates if routes in this controller require protection (e.g., authentication).
        routes (List[Route]): The list of routes collected from the controller's methods.
        controllers (List[Controller]): The list of subcontrollers attached to this controller.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the `Controller` class.

        This constructor collects all methods decorated with HTTP method handlers
        (e.g., GET, POST) and creates corresponding `Route` objects. It also
        collects any middlewares and validation requirements defined on those
        methods, and attaches them to the routes.
        """

        self._base_path: str = getattr(self.__class__, "_base_path", "")
        self._middlewares: List[MiddlewareFunction] = getattr(
            self.__class__, "_middlewares", []
        )
        self._is_protected: str = getattr(self.__class__, "_is_protected", "")
        self.routes: List[Route] = []
        self.controllers: List[Controller] = []

        self._discover_subcontrollers()

        for attr_name in dir(self):
            method = getattr(self, attr_name)

            if attr_name in self.__class__.__dict__ and hasattr(method, "_http_method"):
                middlewares = []

                if hasattr(method, "_middlewares"):
                    middlewares = method._middlewares

                protected = False
                if hasattr(method, "_is_protected"):
                    protected = True

                validate_body = False
                if hasattr(method, "_validate_body"):
                    validate_body = getattr(method, "_validate_body")

                validate_queries = False
                if hasattr(method, "_validate_queries"):
                    validate_queries = getattr(method, "_validate_queries")

                validate_params = False
                if hasattr(method, "_validate_params"):
                    validate_params = getattr(method, "_validate_params")

                produces = None
                if hasattr(method, "_produces"):
                    produces = getattr(method, "_produces")

                openapi_tags: List[str] = []

                if hasattr(self, "_openapi_tags"):
                    openapi_tags = getattr(self, "__openapi_tags")

                if hasattr(method, "_openapi_tags"):
                    openapi_tags = openapi_tags + getattr(method, "_openapi_tags")

                self.routes.append(
                    Route(
                        method,
                        method._http_method,
                        method._sub_route,
                        middlewares,
                        protected,
                        validate_body=validate_body,
                        validate_queries=validate_queries,
                        validate_params=validate_params,
                        produces=produces,
                        openapi_tags=openapi_tags,
                    )
                )

    def _discover_subcontrollers(self) -> None:
        """
        Discovers all subclasses of the current `Controller` class and automatically
        initializes them as subcontrollers.
        """
        subclasses = self.__class__.__subclasses__()

        for subclass in subclasses:
            Logger.debug(f"Discovered Controller {subclass.__name__}")
            self.controllers.append(subclass())

    def resolve_paths(
        self, prefix: str = "", middlewares: List[MiddlewareFunction] = []
    ) -> None:
        """
        Resolve and apply the base paths and middleware to all routes in this controller.

        This method resolves the complete path for each route in the controller
        by combining the provided prefix with the controller's base path. It also
        ensures that any middleware applied to the controller is propagated to its
        routes. If the controller has subcontrollers, their routes are resolved recursively.

        :param prefix: The URL path prefix to prepend to the controller's base path.
        :param middlewares: A list of middleware functions to apply to all routes in the controller.
        """

        new_prefix = prefix.rstrip("/").lstrip("/")
        base_path = self._base_path.lstrip("/")

        if new_prefix:
            new_prefix = f"/{new_prefix}/{base_path}".rstrip("/")
        else:
            new_prefix = f"/{base_path}".rstrip("/")

        for route in self.routes:
            if self._is_protected:
                route.make_protected()

            route.resolve(new_prefix, middlewares + self._middlewares)

        for controller in self.controllers:
            controller.resolve_paths(new_prefix, middlewares + self._middlewares)

    def collect_routes(self) -> Generator[Route, None, None]:
        """
        Collect and yield all routes defined in this controller and its subcontrollers.

        This method generates all routes defined in the controller, including
        those in any attached subcontrollers, recursively.

        :yield: The routes defined in this controller and its subcontrollers.
        """

        yield from self.routes

        for controller in self.controllers:
            yield from controller.collect_routes()
