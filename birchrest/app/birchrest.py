from typing import Dict, List, Optional, Type

from birchrest.exceptions.api_error import ApiError
from birchrest.http.server import Server
from birchrest.routes import Route, Controller
from birchrest.utils.artwork import get_artwork
from ..http import Request, Response, HttpStatus
from ..exceptions import InvalidControllerRegistration
from ..types import MiddlewareFunction, AuthHandlerFunction, ErrorHandler
from birchrest.version import __version__

class BirchRest:
    def __init__(self) -> None:
        self.controllers: List[Controller] = []
        self.global_middlewares: List[MiddlewareFunction] = []
        self.auth_handler: Optional[AuthHandlerFunction] = None
        self.error_handler: Optional[ErrorHandler] = None
            
    def register(self, *controllers: Type[Controller]) -> None:
        for controller in controllers:
            if not issubclass(controller, Controller):
                raise InvalidControllerRegistration(controller)
                        
            self.controllers.append(controller())
            
    def auth(self, auth_handler: AuthHandlerFunction) -> None:
        self.auth_handler = auth_handler
        
    def middleware(self, handler: MiddlewareFunction) -> None:
        self.global_middlewares.append(handler)
        
    def error(self, handler: ErrorHandler) -> None:
        self.error_handler = handler
         
    def serve(self, host: str = "127.0.0.1", port: int = 13337) -> None:
        self._build_api()
        server = Server(self.handle_request, host=host, port=port)
        
        print(get_artwork(host, port, __version__))
        
        try:
            server.start()
        except KeyboardInterrupt:
            print("\nServer shutdown initiated by user. Exiting...")
        finally:
            server.shutdown()
            print("Server stopped.")

        
    def handle_request(self, request: Request) -> Response:
        response = Response(request.correlation_id)
                
        try:
            return self._handle_request(request, response)
        except ApiError as e:
            if self.error_handler:
                self.error_handler(request, response, e)
                return response
            
            return e.convert_to_response(response)
        except Exception as e:
            if self.error_handler:
                self.error_handler(request, response, e)
                return response
                
            return response.status(500).send({
                "error": {
                    "status": 500,
                    "code": "Internal Server Error"
                    }
                })
            
        
    def _handle_request(self, request: Request, response: Response) -> Response:
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

                matched_route(request, response)

        else:

            if route_exists:
                raise ApiError.METHOD_NOT_ALLOWED()
            else:
                raise ApiError.NOT_FOUND()

        return response
                
    def _build_api(self) -> None:
        self.routes = []
        
        for controller in self.controllers:
            controller.resolve_paths(middlewares = self.global_middlewares)
        
        for controller in self.controllers:
            for route in controller.collect_routes():
                route.register_auth_handler(self.auth_handler)
                self.routes.append(route)
