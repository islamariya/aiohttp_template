import uuid
from functools import partial
import time

from aiohttp.web import (Application, middleware,
                         HTTPException, HTTPInternalServerError,
                         json_response,
                         Request)
# from aiohttp_jinja2 import setup
# from jinja2 import FileSystemLoader

from app.api.auth.jwt_security import auth_middleware
from app.api.routes import app_routes

from app.constants.handlers import ResponseType
from app.db.connection import DbConnection
from app.logs.logger import logger
from app.settings import STATIC_DIR, STATIC_PATH, REQUEST_ID_HEADER_NAME


def form_extra_log_request_params(request: Request):
    extra_data = {"method": request.method,
                  "path": request.path,
                  "ip": request.host,
                  "agent": request.headers.get("User-Agent"),
                  "authorization": request.headers.get("Authorization")}
    return extra_data


@logger.catch()
def request_id_middleware():
    @middleware
    async def add_request_id_middleware(request: Request,
                                        handler, *args, **kwargs):
        start_time = time.perf_counter()
        request_id = request.headers.get(REQUEST_ID_HEADER_NAME)
        if not request_id:
            request_id = str(uuid.uuid4())

        with logger.contextualize(request_id=request_id):
            logger.info("'{}' request at '{}' has received", request.method, request.path)
            response = await handler(request, *args, **kwargs)
            response.headers["X-Request-ID"] = request_id
            extra_request_data = form_extra_log_request_params(request=request)
            new_logger = logger.bind(request_data=extra_request_data)
            elapsed_time = time.perf_counter() - start_time
            new_logger.log("STATS", "Request ID {} has processed for {}", request_id, elapsed_time)
        return response

    return add_request_id_middleware


def json_response_middleware():
    @middleware
    async def json_middleware(request, handler, *args, **kwargs):
        try:
            result, status = await handler(request, *args, **kwargs)
            response_data = {"status": ResponseType.ok.value,
                             "result": result}
        except Exception as e:
            request_extra_data = form_extra_log_request_params(request=request)

            if not isinstance(e, HTTPException):
                e = HTTPInternalServerError()

            error_message = e.text
            status = e.status
            error_type = type(e).__name__

            response_data = {"status": ResponseType.error.value,
                             "result": {"error_type": error_type,
                                        "error_message": error_message,
                                        "status": status}}

            enriched_logger = logger.bind(request_data=request_extra_data)
            enriched_logger.info("Error Response has sent: {} - {}", error_type, error_message)

        return json_response(data=response_data,
                             status=status)

    return json_middleware


async def on_startup(app: Application, db_url: str):
    # _t = humanize.i18n.activate("ru_RU")
    db_connection = DbConnection(db_url=db_url)
    app["db"] = db_connection


async def on_cleanup(app: Application):
    await app["db"].stop()


def create_app(db_url) -> Application:
    request_middleware = request_id_middleware()
    json_response_convertor = json_response_middleware()
    app = Application(middlewares=[request_middleware,
                                   json_response_convertor,
                                   auth_middleware])
    app.add_routes(app_routes)
    app.router.add_static(STATIC_PATH,
                          path=STATIC_DIR,
                          name='static')
    # setup(app, loader=FileSystemLoader("core/api/ra_admin/templates"))
    app.on_startup.append(partial(on_startup, db_url=db_url))
    app.on_cleanup.append(on_cleanup)

    return app
