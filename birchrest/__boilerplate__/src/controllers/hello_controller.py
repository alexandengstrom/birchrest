from birchrest import Controller
from birchrest.decorators import controller, get
from birchrest.http import Request, Response

@controller("hello")
class HelloController(Controller):
    
    @get()
    async def say_hello(self, req: Request, res: Response) -> Response:
        return res.status(200).send({"message": "Hello World!"})