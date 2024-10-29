from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, \
                                    AsyncSession, \
                                    async_sessionmaker

from config import setting


a_engine = create_async_engine(
    url=setting.DB_URL,
    echo=False,
    pool_size=5,
    max_overflow=10
)

a_session = async_sessionmaker(a_engine)

class Base(DeclarativeBase):
    pass