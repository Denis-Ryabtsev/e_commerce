from datetime import datetime
import re
from typing import Optional, Union

from fastapi_users import schemas
from pydantic import BaseModel, EmailStr, field_validator

from auth.models import RoleType


email_domain = [
    "@gmail.com",
    "@yahoo.com",
    "@outlook.com",
    "@yandex.ru",
    "@mail.ru",
    "@bk.ru"
]


class UserRead(schemas.BaseUser[int]):
    id: int
    email: str
    username: str
    role: RoleType
    registry_at: datetime
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserCreate(schemas.BaseUserCreate):
    username: str
    email: str
    password: str
    role: RoleType
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserInfo(BaseModel):
    username: str
    role: RoleType
    #Если продавец, то выставить его товар


class MyInfo(BaseModel):
    username: str
    email: str
    role: RoleType
    registry_at: datetime
    is_active: bool
    is_verified: bool


class UserReg(BaseModel):
    user_name: str
    user_email: EmailStr
    user_password: str
    user_role: RoleType

    @field_validator("user_password")
    def validate_passwd(cls, value: str) -> Union[str, Exception]:
        if len(value) < 5 or len(value) > 10:
            raise ValueError(f"Password must contain from 5 to 10 symbols")
        if not re.search(r"[A-Z]", value):
            raise ValueError(f"Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError(f"Password must contain at least one lowercase letter")
        if not re.search(r"\d", value):
            raise ValueError(f"Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError(f"Password must contain at least one special character")
        return value
    
    @field_validator("user_email")
    def validate_email(cls, value: EmailStr) -> Union[None, Exception]:
        domain = value[value.find("@"):]
        if domain not in email_domain:
            raise ValueError(f"Email domain in {value} is not validate")
        return value