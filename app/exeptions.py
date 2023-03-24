from typing import Any

from aiohttp.web_exceptions import (HTTPBadRequest,
                                    HTTPUnauthorized,
                                    HTTPUnprocessableEntity)

from app.constants.exeption_const import ErrorMessages


class NoBodyError(HTTPBadRequest):
    DETAIL = ErrorMessages.EMPTY_BODY

    def __init__(self, **kwargs: dict[str, Any]):
        super().__init__(reason=self.DETAIL, **kwargs)


class SchemaValidationError(HTTPUnprocessableEntity):

    def __init__(self, **kwargs: dict[str, Any]):
        super().__init__(**kwargs)


class PhoneTaken(HTTPBadRequest):
    DETAIL = ErrorMessages.PHONE_TAKEN

    def __init__(self, **kwargs: dict[str, Any]):
        super().__init__(reason=self.DETAIL, **kwargs)


class Unauthorized(HTTPUnauthorized):

    def __init__(self, **kwargs: dict[str, Any]):
        super().__init__(**kwargs)


class InvalidCredentials(HTTPUnauthorized):
    DETAIL = ErrorMessages.INVALID_CREDENTIALS

    def __init__(self, **kwargs: dict[str, Any]):
        super().__init__(reason=self.DETAIL, **kwargs)


class TokenError(HTTPUnauthorized):
    DETAIL = ErrorMessages.TOKEN_NOT_VALID

    def __init__(self, **kwargs: dict[str, Any]):
        super().__init__(reason=self.DETAIL, **kwargs)
