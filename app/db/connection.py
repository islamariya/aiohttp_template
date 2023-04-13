from sqlalchemy.ext.asyncio import (AsyncSession,
                                    async_sessionmaker,
                                    create_async_engine)

from app.settings import settings


def create_postgres_url(settings) -> str:
    template = "{dialect}+{driver}://{user_name}:{password}@{host}/{db_name}"
    return template.format(
            dialect=settings.database_dialect,
            driver=settings.database_driver,
            user_name=settings.postgres_user,
            password=settings.postgres_password,
            host=settings.database_host,
            db_name=settings.database_name
        )


class DbConnection:

    def __init__(self, db_url):

        self.engine = create_async_engine(url=db_url,
                                          echo=False,
                                          future=True)

        self.session_factory = async_sessionmaker(bind=self.engine,
                                                  expire_on_commit=False)

    async def get_database_session(self) -> AsyncSession:
        return self.session_factory()

    async def stop(self):
        await self.engine.dispose()


db_url = create_postgres_url(settings=settings)

db_connection = DbConnection(db_url=db_url)
