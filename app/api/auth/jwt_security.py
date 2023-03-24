import asyncio
import base64
from datetime import datetime, timedelta

from aiohttp.web import middleware
import bcrypt as bcrypt
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID

from app.constants.auth import AUTH_HEADER_NAME, TokenType
from app.constants.exeption_const import ErrorMessages
from app.db.query.user import update_refresh_token_in_db
from app.exeptions import TokenError, Unauthorized
from app.logs.logger import logger
from app.settings import AUTH_WHITE_LIST, JWT_AUTH_SCHEME, settings


def generate_password_hash(password, salt_rounds=12):
    password_bin = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bin, bcrypt.gensalt(salt_rounds))
    encoded = base64.b64encode(hashed)
    return encoded.decode("utf-8")


def check_password_hash(password: str,
                        password_in_db: str) -> bool:
    password_bin = password.encode("utf-8")
    password_hash_bin = password_in_db.encode('utf-8')
    password_hash_bin = base64.b64decode(password_hash_bin)
    is_correct = bcrypt.checkpw(password_bin, password_hash_bin)

    return is_correct


def decode_token(token: str):
    try:
        payload = jwt.decode(jwt=token,
                             key=settings.jwt_token_secret_key,
                             algorithms=[settings.jwt_algorithm],
                             verify=True
                             )

        return payload

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        logger.error("{} - {}", e, token)
        raise TokenError


def create_token(user_id: UUID, exp: int, token_type: TokenType) -> str:
    payload = {"user_id": str(user_id),
               "token_type": token_type.value,
               "exp": datetime.utcnow() + timedelta(seconds=exp)
               }

    return jwt.encode(payload=payload,
                      key=settings.jwt_token_secret_key,
                      algorithm=settings.jwt_algorithm)


async def create_refresh_token(user_id: UUID,
                               session: AsyncSession):
    exp = settings.refresh_jwt_exp_delta_sec
    token_type = TokenType.refresh
    refresh_token = create_token(user_id=user_id,
                                 exp=exp, token_type=token_type)

    token_exp_str = decode_token(token=refresh_token).get("exp")

    refresh_token_expire = datetime.utcfromtimestamp(token_exp_str)

    asyncio.create_task(update_refresh_token_in_db(user_id=user_id,
                                                   token_str=refresh_token,
                                                   exp=refresh_token_expire,
                                                   session=session))
    return refresh_token


async def create_pair_of_tokens(user_id: UUID,
                                session: AsyncSession) -> dict:

    access_token = create_token(user_id=user_id,
                                exp=settings.access_jwt_exp_delta_sec,
                                token_type=TokenType.access)

    refresh_token = await create_refresh_token(user_id=user_id, session=session)

    logger.info("Token pair for user {} has been successfully updated", user_id)

    return {"access": access_token,
            "refresh": refresh_token,
            "token_type": JWT_AUTH_SCHEME,
            "user_id": str(user_id),
            "expires_in": settings.access_jwt_exp_delta_sec}


def get_token_from_request(request) -> str:
    try:
        auth_header = request.headers[AUTH_HEADER_NAME]
        auth_schema, token = auth_header.split()

    except KeyError:
        logger.error("{}: {}", ErrorMessages.AUTH_HEADER_MISSING,
                     request.headers)
        raise Unauthorized(reason=ErrorMessages.AUTH_HEADER_MISSING)

    except ValueError:
        logger.error("{} {}", ErrorMessages.AUTH_HEADER_INVALID, auth_header)
        raise Unauthorized(reason=ErrorMessages.AUTH_HEADER_INVALID)

    if auth_schema != JWT_AUTH_SCHEME:
        logger.error("{}: {}", ErrorMessages.WRONG_AUTH_TYPE,
                     request.headers)
        raise Unauthorized(reason=ErrorMessages.WRONG_AUTH_TYPE)

    return token


def token_middleware():
    @middleware
    async def token_auth_middleware(request, handler):

        if request.rel_url.path in AUTH_WHITE_LIST:
            return await handler(request)

        try:
            token = get_token_from_request(request=request)
        except Unauthorized:
            raise

        payload = decode_token(token=token)

        if payload.get("token_type") != TokenType.access.value:
            logger.error("Refresh token has been used for auth: {}", payload)
            raise TokenError

        return await handler(request)

    return token_auth_middleware


auth_middleware = token_middleware()
