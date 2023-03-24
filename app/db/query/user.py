from typing import Optional

from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models as md
from app.schemas.user import UserCreate
from app.logs.logger import logger


async def get_user_by_phone(session: AsyncSession,
                            phone: str) -> Optional[md.User]:
    async with session.begin():
        query_result = await session.execute(select(md.User).
                                             filter(and_(md.User.phone == phone,
                                                         md.User.is_active)))
        user = query_result.scalar_one_or_none()

    return user


async def create_user(session: AsyncSession,
                      user_data: UserCreate) -> md.User:
    async with session.begin():
        new_user = md.User(**user_data.dict())
        session.add(new_user)
        await session.flush()
    logger.info("User {} has been created successfully", user_data.phone)
    return new_user


async def update_refresh_token_in_db(session: AsyncSession,
                                     user_id: UUID,
                                     exp: datetime,
                                     token_str: str):

    async with session.begin():
        query_result = await session.execute(select(md.Token).
                                             filter(md.Token.owner_id == user_id))
        token = query_result.scalar_one_or_none()
        if token:
            await session.delete(token)
        session.add(md.Token(owner_id=user_id, key=token_str, valid_till=exp))
        await session.flush()
