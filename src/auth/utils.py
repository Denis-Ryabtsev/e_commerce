from typing import AsyncGenerator

from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi import Depends

from auth.models import User
from database import get_async_session


async def get_user_db(session: AsyncGenerator = Depends(get_async_session)) \
                                                        -> AsyncGenerator:
    yield SQLAlchemyUserDatabase(session, User)