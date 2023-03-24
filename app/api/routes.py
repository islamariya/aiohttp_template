from aiohttp import web

from app.api.auth.routes import auth_routes
from app.api.handlers import Handler


app_routes = [web.get("/", Handler.main_page, name="main")]

app_routes += auth_routes
