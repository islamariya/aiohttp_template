import uuid

from sqlalchemy import (Boolean, Column, DateTime, func)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr, declarative_base


class Base:
    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, unique=True, index=True)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


base = declarative_base(cls=Base)


class TimeStampMixin:
    created_dt = Column(DateTime(timezone=True), default=func.now())


class ActivatedMixin:
    is_active = Column(Boolean, default=True)
