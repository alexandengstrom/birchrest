import re
from typing import Any, Dict, List, Optional, Tuple

from birchrest.exceptions.api_error import ApiError
from birchrest.routes.validator import parse_data_class
from ..types import RouteHandler, MiddlewareFunction, AuthHandlerFunction
from ..http import Request, Response
from ..exceptions import MissingAuthHandlerError


class Route:
    """
    Represents an HTTP route in the application, mapping a specific HTTP method and path
    to a handler function. A `Route` can have middlewares, be protected with authentication,
    and validate request bodies, query parameters, and URL parameters.

    Attributes:
        func (RouteHandler): The handler function to execute when the route is matched.
        method (str): The HTTP method for this route (e.g., GET, POST).
        path (str): The URL path pattern for this route (e.g., '/users/:id').
        middlewares (List[MiddlewareFunction]): A list of middleware functions to run before the handler.
        is_protected (bool): Indicates if this route requires authentication.
        validate_body (Optional[Any]): A dataclass or schema to validate the request body.
        validate_queries (Optional[Any]): A dataclass or schema to validate the query parameters.
        validate_params (Optional[Any]): A dataclass or schema to validate the URL parameters.
        auth_handler (Optional[AuthHandlerFunction]): A function to handle authentication for protected routes.
    """

    def __init__(
        self,
        func: RouteHandler,
        method: str,
        path: str,
        middlewares: List[MiddlewareFunction],
        protected: bool,
        validate_body: Optional[Any],
        validate_queries: Optional[Any],
        validate_params: Optional[Any],
    ) -> None:
        """
        Initializes a new `Route` object with the provided handler, method, path, and configurations.

        :param func: The handler function to be executed when the route is matched.
        :param method: The HTTP method (GET, POST, etc.) for this route.
        :param path: The URL path for this route, which may include dynamic parameters (e.g., '/users/:id').
        :param middlewares: A list of middleware functions to apply to this route.
        :param protected: Whether the route requires authentication.
        :param validate_body: A dataclass or schema to validate the request body, if applicable.
        :param validate_queries: A dataclass or schema to validate the query parameters, if applicable.
        :param validate_params: A dataclass or schema to validate the URL parameters, if applicable.
        """

        self.func = func
        self.method = method
        self.path = path
        self.middlewares = middlewares
        self.is_protected = protected
        self.validate_body = validate_body
        self.validate_queries = validate_queries
        self.validate_params = validate_params
        self.auth_handler: Optional[AuthHandlerFunction] = None
        self.param_names: List[Any] = []
        self.requires_params = 0
        self.regex = re.compile(".*")

    def resolve(self, prefix: str, middlewares: List[MiddlewareFunction]) -> None:
        """
        Resolves the final path and middlewares for the route, combining the given prefix
        with the route's path and appending any global middlewares.

        :param prefix: The path prefix to prepend to the route's path.
        :param middlewares: A list of global middleware functions to apply before the route-specific middlewares.
        """

        new_prefix = prefix.rstrip("/")
        self.path = f"{new_prefix}/{self.path.lstrip('/')}"
        print(self.path)
        self.middlewares = middlewares + self.middlewares

        path_regex = re.sub(r":(\w+)", r"(?P<\1>[^/]+)", self.path)

        path_regex = f"^{path_regex}$"
        self.param_names = re.findall(r":(\w+)", self.path)
        self.requires_params = len(self.param_names) > 0
        self.regex = re.compile(path_regex)

    def __call__(self, req: Request, res: Response) -> Any:
        """
        Executes the route's middleware stack and handler function when the route is matched.

        This method checks if the route is protected and performs authentication if needed.
        It also validates the request body, query parameters, and URL parameters if validation
        is enabled. Finally, it executes the route handler.

        :param req: The incoming HTTP request.
        :param res: The outgoing HTTP response.
        :raises ApiError: If authentication or validation fails.
        :return: The result of the route handler function.
        """

        if self.is_protected:
            if not self.auth_handler:
                raise MissingAuthHandlerError()

            try:
                user_data = self.auth_handler(req, res)

                if not user_data:
                    raise ApiError.UNAUTHORIZED()

                req.user = user_data
            except Exception as e:
                raise ApiError.UNAUTHORIZED() from e

        if self.validate_body:
            try:
                body_data = req.body
                if not body_data:
                    raise ApiError.BAD_REQUEST("Request body is required")

                parsed_data = parse_data_class(self.validate_body, body_data)

                req.body = parsed_data

            except ValueError as e:
                raise ApiError.BAD_REQUEST(f"Body validation failed: {str(e)}")

        if self.validate_queries:
            try:
                parsed_data = parse_data_class(self.validate_queries, req.queries)

                req.queries = parsed_data

            except ValueError as e:
                raise ApiError.BAD_REQUEST(f"Query validation failed: {str(e)}")

        if self.validate_params:
            try:
                parsed_data = parse_data_class(self.validate_params, req.params)

                req.queries = parsed_data

            except ValueError as e:
                raise ApiError.BAD_REQUEST(f"Param validation failed: {str(e)}")

        def run_middlewares(index: int) -> Any:
            if index < len(self.middlewares):
                middleware = self.middlewares[index]
                return middleware(req, res, lambda: run_middlewares(index + 1))
            else:
                return self.func(req, res)

        return run_middlewares(0)

    def match(self, request_path: str) -> Optional[Dict[str, str]]:
        """
        Checks if the given request path matches the route's path pattern.

        :param request_path: The incoming request path.
        :return: A dictionary of matched parameters if the path matches, otherwise None.
        """

        match = self.regex.match(request_path)
        if match:
            return match.groupdict()
        return None

    def is_method_allowed(self, method: str) -> bool:
        """
        Checks if the given HTTP method is allowed for this route.

        :param method: The HTTP method (e.g., GET, POST) to check.
        :return: True if the method is allowed, otherwise False.
        """

        return method == self.method

    def register_auth_handler(
        self, auth_handler: Optional[AuthHandlerFunction]
    ) -> None:
        """
        Registers an authentication handler for this route.

        :param auth_handler: A function that handles authentication for protected routes.
        """

        self.auth_handler = auth_handler

    def make_protected(self) -> None:
        """
        Marks the route as protected, requiring authentication to access.
        """

        self.is_protected = True
