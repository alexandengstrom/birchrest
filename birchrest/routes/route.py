import re
from typing import List, Tuple

from birchrest.routes.validator import parse_data_class
from ..types import RouteHandler, MiddlewareFunction
from ..http import Request, Response
from ..exceptions import MissingAuthHandlerError


class Route:
    def __init__(self, 
                 func: RouteHandler, 
                 method: str, 
                 path: str, 
                 middlewares: List[MiddlewareFunction], 
                 protected: bool,
                 validate_body,
                 validate_queries,
                 validate_params,
                 ):
        self.func = func
        self.method = method
        self.path = path
        self.middlewares = middlewares
        self.is_protected = protected
        self.validate_body = validate_body
        self.validate_queries = validate_queries
        self.validate_params = validate_params
        
    def resolve(self, prefix: str, middlewares: List[MiddlewareFunction]):
        new_prefix = "" if not prefix else f"{prefix}/"
        self.path = f"{new_prefix}{self.path}"
        self.middlewares = middlewares + self.middlewares
        
        path_regex = re.sub(r':(\w+)', r'(?P<\1>[^/]+)', self.path)

        path_regex = f"^{path_regex}$"
        self.param_names = re.findall(r':(\w+)', self.path)
        self.requires_params = len(self.param_names) > 0
        self.regex = re.compile(path_regex)
        
    def __call__(self, req: Request, res: Response):
        if self.is_protected:
            if not self.auth_handler:
                raise MissingAuthHandlerError()
            
            try:
                user_data = self.auth_handler(req)
                
                if not user_data:
                    return res.status(401).send({"error": "Unauthorized"})
                
                req.user = user_data
            except:
                return res.status(401).send({"error": "Unauthorized"})

        if self.validate_body:
            try:
                body_data = req.body
                if not body_data:
                    return res.status(400).send({"error": "Request body is required"})

                parsed_data = parse_data_class(self.validate_body, body_data)

                req.body = parsed_data
        
            except ValueError as e:
                return res.status(400).send({"error": f"Body validation failed: {str(e)}"})
            
        if self.validate_queries:
            try:
                parsed_data = parse_data_class(self.validate_queries, req.queries)

                req.queries = parsed_data
        
            except ValueError as e:
                return res.status(400).send({"error": f"Query validation failed: {str(e)}"})
            
        if self.validate_params:
            try:
                parsed_data = parse_data_class(self.validate_params, req.params)

                req.queries = parsed_data
        
            except ValueError as e:
                return res.status(400).send({"error": f"Param validation failed: {str(e)}"})
                
            
        
        def run_middlewares(index):
            if index < len(self.middlewares):
                middleware = self.middlewares[index]
                middleware(req, res, lambda: run_middlewares(index + 1))
            else:
                return self.func(req, res)
        
        return run_middlewares(0)
    
    def match(self, request_path: str):
        match = self.regex.match(request_path)
        if match:
            return match.groupdict()
        return None
    
    def is_method_allowed(self, method: str):
        return method == self.method
    
    def register_auth_handler(self, auth_handler):
        self.auth_handler = auth_handler
        
    def make_protected(self):
        self.is_protected = True
        
        