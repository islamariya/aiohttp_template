from dotenv import load_dotenv
from pydantic import BaseSettings
from os import path


ROOT_DIR = path.dirname(path.abspath(__file__))

LOG_DIR = path.join(ROOT_DIR, "logs", "data")

STATIC_DIR = path.join(ROOT_DIR, "")
STATIC_PATH = "/static/"

MEDIA_DIR = path.join(ROOT_DIR, "media")

TIMEZONE = "Asia/Yekaterinburg"
DT_PATTERN = "%d.%m.%Y %H:%M"

AUTH_WHITE_LIST = ["/auth/signup",
                   "/auth/token",
                   "/auth/refresh"]

JWT_AUTH_SCHEME = "Bearer"

REQUEST_ID_HEADER_NAME = "X-Request-Id"

load_dotenv()


class Config(BaseSettings):
    api_server_host: str
    api_server_port: int

    jwt_token_secret_key: str
    access_jwt_exp_delta_sec: int
    refresh_jwt_exp_delta_sec: int
    jwt_algorithm: str
    reset_password_exp_delta_sec: int

    database_name: str
    database_host: str
    postgres_user: str
    postgres_password: str
    database_dialect: str = "postgresql"
    database_driver: str = "asyncpg"

    class Config:
        env_file = "../.env"


settings = Config()
