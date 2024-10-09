import re
from typing import Any, Dict, List, Optional, Tuple

from birchrest.exceptions.api_error import ApiError
from birchrest.routes.validator import parse_data_class
from ..types import RouteHandler, MiddlewareFunction, AuthHandlerFunction
from ..http import Request, Response
from ..exceptions import MissingAuthHandlerError


class Route:
    def __init__(self, 
                 func: RouteHandler, 
                 method: str, 
                 path: str, 
                 middlewares: List[MiddlewareFunction], 
                 protected: bool,
                 validate_body: Optional[Any],
                 validate_queries: Optional[Any],
                 validate_params: Optional[Any],
                 ) -> None:
        self.func = func
        self.method = method
        self.path = path
        self.middlewares = middlewares
        self.is_protected = protected
        self.validate_body = validate_body
        self.validate_queries = validate_queries
        self.validate_params = validate_params
        self.auth_handler: Optional[AuthHandlerFunction] = None
        
    def resolve(self, prefix: str, middlewares: List[MiddlewareFunction]) -> None:
        new_prefix = prefix.rstrip('/')
        self.path = f"{new_prefix}/{self.path.lstrip('/')}"
        self.middlewares = middlewares + self.middlewares
        
        path_regex = re.sub(r':(\w+)', r'(?P<\1>[^/]+)', self.path)

        path_regex = f"^{path_regex}$"
        self.param_names = re.findall(r':(\w+)', self.path)
        self.requires_params = len(self.param_names) > 0
        self.regex = re.compile(path_regex)
        
    def __call__(self, req: Request, res: Response) -> Any:
        if self.is_protected:
            if not self.auth_handler:
                raise MissingAuthHandlerError()
            
            try:
                user_data = self.auth_handler(req, res)
                
                if not user_data:
                    raise ApiError.UNAUTHORIZED()
                
                req.user = user_data
            except:
                raise ApiError.UNAUTHORIZED()

        if self.validate_body:
            try:
                body_data = req.body
                if not body_data:
                    raise ApiError.BAD_REQUEST(f"Request body is required")

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
        match = self.regex.match(request_path)
        if match:
            return match.groupdict()
        return None
    
    def is_method_allowed(self, method: str) -> bool:
        return method == self.method
    
    def register_auth_handler(self, auth_handler: Optional[AuthHandlerFunction]) -> None:
        self.auth_handler = auth_handler
        
    def make_protected(self) -> None:
        self.is_protected = True
        
        