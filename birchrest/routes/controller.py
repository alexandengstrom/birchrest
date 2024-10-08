from typing import List
from .route import Route
from ..types import MiddlewareFunction

class Controller:
    def __init__(self):
        self._base_path: str = getattr(self.__class__, "_base_path", "")
        self._middlewares: List[MiddlewareFunction] = getattr(self.__class__, "_middlewares", [])
        self._is_protected: str = getattr(self.__class__, "_is_protected", "")
        self.routes: List[Route] = []
        self.controllers: List[Controller] = []
        
        for attr_name in dir(self):
            method = getattr(self, attr_name)
            
            if hasattr(method, '_http_method'):
                middlewares = []
                
                if hasattr(method, "_middlewares"):
                    middlewares = method._middlewares
                 
                protected = False   
                if hasattr(method, '_is_protected'):
                    protected = True
                    
                validate_body = False
                if hasattr(method, '_validate_body'):
                    validate_body = getattr(method, "_validate_body")
                    
                validate_queries = False
                if hasattr(method, '_validate_queries'):
                    validate_queries = getattr(method, "_validate_queries")
                    
                validate_params = False
                if hasattr(method, '_validate_params'):
                    validate_params = getattr(method, "_validate_params")
                                        
                self.routes.append(Route(method, 
                                         method._http_method, 
                                         method._sub_route, 
                                         middlewares, 
                                         protected,
                                         validate_body,
                                         validate_queries,
                                         validate_params
                                         ))
                
    def attach(self, *controllers):
        for controller in controllers:            
            self.controllers.append(controller())
            
    def resolve_paths(self, prefix: str = "", middlewares: List[MiddlewareFunction] = []):
        new_prefix = f"{prefix}/{self._base_path}"
        
        for route in self.routes:
            route.make_protected()
            route.resolve(new_prefix, middlewares + self._middlewares)
            
        for controller in self.controllers:
            controller.resolve_paths(new_prefix, middlewares + self._middlewares)
            
    def collect_routes(self):
        for route in self.routes:
            yield route
            
        for controller in self.controllers:
            yield from controller.collect_routes()