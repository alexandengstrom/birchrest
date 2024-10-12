from birchrest import BirchRest
from example.database import get_user, get_users

app = BirchRest()
app.serve()
