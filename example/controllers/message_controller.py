from example.controllers.user_controller import UserController
from birchrest.decorators import controller, get, params
from birchrest.http import Request, Response
from example.database import get_messages
from example.models import UserId

@controller(":id/messages")
class MessageController(UserController):
    
    @get()
    @params(UserId)
    async def get_user_messages(self, req: Request, res: Response) -> Response:
        messages = await get_messages(req.params.id)
        return res.send(messages)