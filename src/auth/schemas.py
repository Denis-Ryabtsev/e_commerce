from datetime import datetime
from typing import Optional

from fastapi_users import schemas
from auth.models import RoleType


class UserRead(schemas.BaseUser[int]):
    id: int
    email: str
    username: str
    role: RoleType
    registry_at: datetime
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
#вывести параметры superuser и тд

class UserCreate(schemas.BaseUserCreate):
    username: str
    email: str
    password: str
    role: RoleType

# from typing import Optional

# from fastapi_users import schemas


# class UserRead(schemas.BaseUser[int]):
#     id: int
#     email: str
#     username: str
#     role_id: int
#     is_active: bool = True
#     is_superuser: bool = False
#     is_verified: bool = False


# class UserCreate(schemas.BaseUserCreate):
#     username: str
#     email: str
#     password: str
#     role_id: int
#     is_active: Optional[bool] = True
#     is_superuser: Optional[bool] = False
#     is_verified: Optional[bool] = False
