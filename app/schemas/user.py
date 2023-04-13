from uuid import uuid4
from datetime import datetime

from pydantic import BaseModel, constr, EmailStr, Field, UUID4, validator

from typing import Optional

from app.db.enums import UserRoles
from app.utils.dt import convert_dt_to_str


class UserCreate(BaseModel):
    first_name: str = Field(max_length=40)
    last_name: str = Field(max_length=120)
    email: EmailStr
    phone: str = Field(max_length=10)
    role: Optional[UserRoles]
    password: str

    @validator("role", always=True)
    def set_user_role(cls, role):
        if role is None:
            return UserRoles.operator
        return UserRoles(role)


class UserAuth(BaseModel):
    user_name: str = Field(max_length=10)
    password: str


class UserTokenRefresh(BaseModel):
    user_id: UUID4
    refresh_token: str


class UserOut(BaseModel):
    id: UUID4 = Field(default_factory=uuid4())
    phone: str
    created_at: datetime

    @validator("id")
    def validate_uuid(cls, value):
        if value:
            return str(value)

    @validator("created_at")
    def validate_created_at(cls, value):
        if value:
            return convert_dt_to_str(datetime_stmt=value)

    class Config:
        orm_mode = True
