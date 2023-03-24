from typing import Type

from pydantic import BaseModel, ValidationError

from app.exeptions import NoBodyError, SchemaValidationError
from app.logs.logger import logger


class BaseHandler:

    @classmethod
    async def get_db_session(cls, request):
        return await request.app["db"].get_database_session()

    @classmethod
    def validate_empty_body(cls, request):
        if not request.body_exists:
            raise NoBodyError

    @classmethod
    def validate_schema(cls, form_data: dict,
                        schema: Type[BaseModel]):

        try:
            schema_obj = schema(**form_data)
            return schema_obj

        except ValidationError as e:
            message = ""
            for error in e.errors():
                field = error.get("loc")[0]
                reason = error.get("msg")
                message += f"{field} {reason}, "
            logger.error("Ошибка валидации схемы {}: {}", schema.__name__, message)
            raise SchemaValidationError(reason=message)


class Handler(BaseHandler):

    @classmethod
    async def main_page(cls, request):
        return "Hello world", 200
