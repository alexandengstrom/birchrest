from birchrest import BirchRest
from example.database import get_user, get_users
from example.user_controller.user_controller import UserController

app = BirchRest()
app.register(UserController)
app.serve()
