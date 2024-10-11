from birchrest import Middleware
from birchrest.http import Request, Response
from birchrest.types import NextFunction
from birchrest.exceptions import ApiError

class QueryBlocker(Middleware):
    async def __call__(self, req: Request, res: Response, next: NextFunction) -> None:
        if req.queries:
            raise ApiError.BAD_REQUEST("Queries not allowed on this route!")
        
        await next()
            