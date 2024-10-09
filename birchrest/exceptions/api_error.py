from typing import Type

from birchrest.http.response import Response
from birchrest.http.status import HttpStatus

class ApiError(Exception):
    def __init__(self, user_message: str, status_code: int) -> None:
        super().__init__(user_message)
        self.base_message: str = HttpStatus.description(status_code)
        self.user_message: str = user_message
        self.status_code: int = status_code

    def __str__(self) -> str:
        return f"[{self.status_code}] {self.user_message}"
    
    def convert_to_response(self, res: Response) -> Response:
        payload = {
            "error": {
                "status": self.status_code,
                "code": self.base_message,
                "correlationId": res.correlation_id
            }
        }
        
        if self.user_message:
            payload["error"]["message"] = self.user_message
        
        return res.status(self.status_code).send(payload)

    @staticmethod
    def BAD_REQUEST(user_message: str = "") -> 'ApiError':
        return ApiError(user_message, 400)

    @staticmethod
    def UNAUTHORIZED(user_message: str = "") -> 'ApiError':
        return ApiError(user_message, 401)

    @staticmethod
    def FORBIDDEN(user_message: str = "") -> 'ApiError':
        return ApiError(user_message, 403)

    @staticmethod
    def NOT_FOUND(user_message: str = "") -> 'ApiError':
        return ApiError(user_message, 404)
    
    @staticmethod
    def METHOD_NOT_ALLOWED(user_message: str = "") -> 'ApiError':
        return ApiError(user_message, 405)

    @staticmethod
    def INTERNAL_SERVER_ERROR(user_message: str = "") -> 'ApiError':
        return ApiError(user_message, 500)
    
