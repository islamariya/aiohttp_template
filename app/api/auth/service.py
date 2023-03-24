from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth.jwt_security import (check_password_hash,
                                       decode_token,
                                       generate_password_hash,)
from app.constants.auth import TokenType
from app.db.models.user import User
from app.db.query.user import create_user, get_user_by_phone
from app.exeptions import InvalidCredentials, PhoneTaken
from app.logs.logger import logger
from app.schemas.user import UserAuth, UserCreate, UserOut, UserTokenRefresh


async def create_user_service(session: AsyncSession,
                              user_data: UserCreate) -> UserOut:

    password_hash = generate_password_hash(password=user_data.password)
    user_data.password = password_hash

    if await get_user_by_phone(session=session, phone=user_data.phone):
        logger.error("Phone number {} is unavailable", user_data.phone)
        raise PhoneTaken

    user = await create_user(session=session,
                             user_data=user_data)

    return UserOut(id=user.id, phone=user.phone,
                   created_at=user.created_dt)


async def authenticate_user(session: AsyncSession,
                            user_data: UserAuth) -> User:

    user = await get_user_by_phone(session=session,
                                   phone=user_data.user_name)

    if not user:
        logger.error("User {} is  not found or inactive", user_data.user_name)
        raise InvalidCredentials

    if not check_password_hash(password=user_data.password,
                               password_in_db=user.password):
        logger.error("Invalid Credentials {}", user_data.user_name)
        raise InvalidCredentials

    logger.info("User {} has logged in successfully", user.phone)

    return user


async def validate_refresh_token(token_data: UserTokenRefresh):
    payload = decode_token(token=token_data.refresh_token)
    if token_data.user_id != payload.get("user_id"):
        logger.error("User Id {} does not match token", token_data.user_id)
        raise InvalidCredentials

    if payload.get("token_type") != TokenType.refresh.value:
        logger.error("Not refresh token has been provided, but {}",
                     {payload.get("token_type")})
        raise InvalidCredentials
