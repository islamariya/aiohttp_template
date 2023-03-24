from aiohttp.web import run_app

from settings import settings
from server import create_app


def launch_app():
    app = create_app()

    run_app(app=app,
            host=settings.api_server_host,
            port=settings.api_server_port,
            access_log=None)


if __name__ == "__main__":
    launch_app()
