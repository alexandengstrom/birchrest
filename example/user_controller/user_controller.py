from birchrest import Controller
from birchrest.decorators import get, post, controller, params, middleware, body
from birchrest.http import Request, Response
from birchrest.exceptions import ApiError
from example.database import get_user, get_users, create_user
from example.models import UserId, UserModel
from example.middlewares.query_blocker import QueryBlocker
from dataclasses import asdict


@controller("user")
class UserController(Controller):

    @get(":id")
    @params(UserId)
    async def get_user(self, req: Request, res: Response) -> Response:
        user = await get_user(req.params.id)

        if user:
            return res.status(200).send(user)
        else:
            raise ApiError.NOT_FOUND(f"No user with id {req.params.id} exists")

    @get()
    @middleware(QueryBlocker())
    async def get_users(self, req: Request, res: Response) -> Response:
        users = await get_users()
        return res.status(200).send(users)

    @post()
    @body(UserModel)
    async def post_user(self, req: Request, res: Response) -> Response:
        await create_user(asdict(req.body))
        return res.status(201).send()
