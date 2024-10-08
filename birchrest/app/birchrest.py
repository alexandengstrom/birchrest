from typing import Dict, Optional

from birchrest.http.server import Server
from birchrest.routes import Route, Controller
from ..http import Request, Response, HttpStatus
from ..exceptions import InvalidControllerRegistration
from ..types import MiddlewareFunction

class BirchRest:
    def __init__(self):
        self.controllers = []
        self.global_middlewares = []
        self.auth_handler = None
            
    def register(self, *controllers):
        for controller in controllers:
            if not issubclass(controller, Controller):
                raise InvalidControllerRegistration(controller)
                        
            self.controllers.append(controller())
            
    def auth(self, auth_handler):
        self.auth_handler = auth_handler
        
    def middleware(self, handler: MiddlewareFunction):
        self.global_middlewares.append(handler)
         
    def serve(self, host="127.0.0.1", port=13337):
        self._build_api()
        server = Server(self.handle_request, host=host, port=port)
        server.start()
        
    def handle_request(self, request: Request):
        response = Response()
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
                response.status(400).send(
                    {"error": "400 Bad Request - Missing Parameters"}
                )
            else:

                request.params = path_params if path_params is not None else {}

                matched_route(request, response)
        else:

            if route_exists:
                response.status(405).send({"error": "405 Method Not Allowed"})
            else:

                response.status(404).send({"error": "404 Not Found"})

        return response
                
    def _build_api(self):
        self.routes = []
        
        for controller in self.controllers:
            controller.resolve_paths(middlewares = self.global_middlewares)
        
        for controller in self.controllers:
            for route in controller.collect_routes():
                route.register_auth_handler(self.auth_handler)
                self.routes.append(route)
