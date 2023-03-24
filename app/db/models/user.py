from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.db.enums import UserRoles
from app.db.models.base import ActivatedMixin, base, TimeStampMixin


class User(base, ActivatedMixin, TimeStampMixin):
    """логин это номер телефона"""
    first_name = Column(String(40), nullable=False)
    last_name = Column(String(120), nullable=False)
    email = Column(String(254), nullable=False)
    phone = Column(String(10), unique=True, nullable=False)
    role = Column(Enum(UserRoles), default=UserRoles.operator, nullable=False)
    password = Column(String, nullable=False)


class Token(base, TimeStampMixin):
    key = Column(String())
    owner_id = Column(UUID(as_uuid=True), ForeignKey(User.id))
    valid_till = Column(DateTime(timezone=True))

    def __init__(self, key: str, owner_id: UUID, valid_till: datetime):
        self.key = key
        self.owner_id = owner_id
        self.valid_till = valid_till
