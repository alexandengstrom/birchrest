from dataclasses import is_dataclass
import re
from typing import Any, Dict, List, Optional
from birchrest.exceptions.invalid_validation_model import InvalidValidationModel
from birchrest.routes.validator import parse_data_class
from birchrest.utils import dict_to_dataclass
from ..types import RouteHandler, MiddlewareFunction, AuthHandlerFunction
from ..http import Request, Response
from ..exceptions import MissingAuthHandlerError, Unauthorized, BadRequest
from ..utils import Logger


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
        produces: Optional[Any] = None,
        openapi_tags: List[str] = []
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
        :param produces: A dataclass or schema to show what the route returns.
        """

        self.func = func
        self.method = method
        self.path = path
        self.middlewares = middlewares
        self.is_protected = protected
        self.validate_body = validate_body
        self.validate_queries = validate_queries
        self.validate_params = validate_params
        self.produces = produces
        self.openapi_tags = openapi_tags
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
        self.path = f"{new_prefix}/{self.path.lstrip('/')}".rstrip("/")

        Logger.debug(f"Generated route {self.path}")

        self.middlewares = middlewares + self.middlewares

        path_regex = re.sub(r":(\w+)", r"(?P<\1>[^/]+)", self.path)

        path_regex = f"^{path_regex}$"
        self.param_names = re.findall(r":(\w+)", self.path)
        self.requires_params = len(self.param_names) > 0
        self.regex = re.compile(path_regex)

    async def __call__(self, req: Request, res: Response) -> Any:
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
                auth_result = await self.auth_handler(req, res)

                if not auth_result:
                    Logger.debug(
                        f"Request to {self.path} from {req.client_address} was rejected"
                    )
                    raise Unauthorized

                req.user = auth_result
            except Exception as e:
                Logger.debug(
                    f"Request to {self.path} from {req.client_address} was rejected"
                )
                raise Unauthorized from e

        if self.validate_body:
            try:
                body_data = req.body
                if not body_data:
                    Logger.debug(
                        f"Request to {self.path} from {req.client_address} failed body validation"
                    )
                    raise BadRequest("Request body is required")

                if isinstance(self.validate_body, type) and is_dataclass(
                    self.validate_body
                ):
                    parsed_data = parse_data_class(self.validate_body, body_data)
                    req.body = parsed_data

                else:
                    raise InvalidValidationModel(self.validate_body)

            except ValueError as e:
                Logger.debug(
                    f"Request to {self.path} from {req.client_address} failed body validation"
                )
                raise BadRequest(f"Body validation failed: {str(e)}") from e
        else:
            req.body = dict_to_dataclass("body", req.body)

        if self.validate_queries:
            try:
                if isinstance(self.validate_body, type) and is_dataclass(
                    self.validate_body
                ):
                    parsed_data = parse_data_class(self.validate_body, body_data)
                    req.queries = parsed_data

                else:
                    raise InvalidValidationModel(self.validate_queries)

            except ValueError as e:
                Logger.debug(
                    f"Request to {self.path} from {req.client_address} failed query validation"
                )
                raise BadRequest(f"Query validation failed: {str(e)}")
        else:
            req.queries = dict_to_dataclass("queries", req.queries)

        if self.validate_params:
            try:
                if isinstance(self.validate_params, type) and is_dataclass(
                    self.validate_params
                ):
                    parsed_data = parse_data_class(self.validate_params, req.params)
                    req.params = parsed_data

                else:
                    raise InvalidValidationModel(self.validate_params)

            except ValueError as e:
                Logger.debug(
                    f"Request to {self.path} from {req.client_address} failed param validation"
                )
                raise BadRequest(f"Param validation failed: {str(e)}")
        else:
            req.params = dict_to_dataclass("params", req.params)

        async def run_middlewares(index: int) -> None:
            if index < len(self.middlewares):
                middleware = self.middlewares[index]
                await middleware(req, res, lambda: run_middlewares(index + 1))
            else:
                await self.func(req, res)

        return await run_middlewares(0)

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
        Logger.debug(f"Route {self.path} was marked as protected")
        self.is_protected = True
