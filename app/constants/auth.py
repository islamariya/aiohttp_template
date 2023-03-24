from app.db.enums import BaseEnum


class TokenType(BaseEnum):
    refresh = "refresh"
    access = "access"


AUTH_HEADER_NAME = "Authorization"
