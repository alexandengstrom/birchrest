from birchrest import Controller
from birchrest.decorators import controller, get, params
from birchrest.http import Request, Response
from example.database import get_messages
from example.models import UserId

@controller("health")
class MessageController(Controller):
    
    @get()
    async def health(self, req: Request, res: Response) -> Response:
        return res.send({"message": "Service is healthy!"})