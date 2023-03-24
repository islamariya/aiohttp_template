from aiohttp import web

from app.api.auth.views import Handler


auth_routes = [web.post("/auth/signup", Handler.create_user, name="create_user"),
               web.post("/auth/token", Handler.auth_user, name="obtain_token"),
               web.post("/auth/refresh", Handler.refresh_token, name="refresh_token"),
               ]
