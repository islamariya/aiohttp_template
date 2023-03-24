from aiohttp import web

from app.api.handlers import BaseHandler
from app.api.auth.service import (authenticate_user,
                                  create_user_service,
                                  validate_refresh_token)
from app.api.auth.jwt_security import create_pair_of_tokens
from app.logs.logger import logger
from app.schemas.user import UserAuth, UserCreate, UserTokenRefresh


class Handler(BaseHandler):

    @classmethod
    async def create_user(cls, request: web.Request):
        """
        :raises
        NoBodyError
        PhoneTaken
        SchemaValidationError
        """
        cls.validate_empty_body(request=request)
        post_data = await request.json()
        user_data = cls.validate_schema(form_data=post_data, schema=UserCreate)
        logger.info("User schema has been generated successfully {}",
                    user_data.phone)
        session = await cls.get_db_session(request)
        user_data = await create_user_service(session=session, user_data=user_data)

        return user_data.dict(), 201

    @classmethod
    async def auth_user(cls, request):
        """Этот метод проводит идентификацию и аутентификацию пользователя,
        при успехе выдает пару токенов"""

        cls.validate_empty_body(request=request)
        post_data = await request.json()
        user_data = cls.validate_schema(form_data=post_data, schema=UserAuth)

        logger.info("User schema has been generated successfully {}",
                    user_data.user_name)

        session = await cls.get_db_session(request)

        auth_user = await authenticate_user(session=session,
                                            user_data=user_data)

        token_pair = await create_pair_of_tokens(user_id=auth_user.id,
                                                 session=session)

        return token_pair, 200

    @classmethod
    async def refresh_token(cls, request):

        cls.validate_empty_body(request=request)
        post_data = await request.json()
        token_data = cls.validate_schema(form_data=post_data,
                                         schema=UserTokenRefresh)
        logger.info("User token schema has been generated successfully {}",
                    token_data.user_id)

        session = await cls.get_db_session(request)

        await validate_refresh_token(token_data=token_data)

        token_pair = await create_pair_of_tokens(user_id=token_data.user_id,
                                                 session=session)

        return token_pair, 200
