from typing import List
from birchrest import Controller
from birchrest.decorators import (
    get,
    post,
    controller,
    params,
    middleware,
    body,
    produces,
    tag
)
from birchrest.http import Request, Response
from birchrest.exceptions import NotFound
from example.database import get_user, get_users, create_user
from example.models import UserId, UserModel, UserResponseModel, UsersModel
from dataclasses import asdict


@controller("user")
class UserController(Controller):

    @get(":id")
    @params(UserId)
    @produces(UserResponseModel)
    @tag("User")
    async def get_user(self, req: Request, res: Response) -> Response:
        user = await get_user(req.params.id)

        if user:
            return res.status(200).send(user)
        else:
            raise NotFound(f"No user with id {req.params.id} exists")

    @get()
    @body(UsersModel)
    @tag("User")
    async def get_users(self, req: Request, res: Response) -> Response:
        users = await get_users()
        return res.status(200).send(users)

    @post()
    @body(UserModel)
    @tag("User")
    async def post_user(self, req: Request, res: Response) -> Response:
        await create_user(asdict(req.body))
        return res.status(201).send()
