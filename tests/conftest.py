import asyncio
import pytest

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from fastapi_users.jwt import generate_jwt
from fastapi_users.db import SQLAlchemyUserDatabase

from database import get_async_session, a_engine, Base
from config import setting
from auth.models import User
from auth.schemas import UserCreate
from auth.manager import UserManager
from main import app


engine_test = create_async_engine(
    url=setting.DB_URL,
    pool_size=5,
    max_overflow=10, 
    echo=False
)

engine_db = create_async_engine(
    url=setting.DB_URL,
    pool_size=5,
    max_overflow=10,  
    echo=False
)

AsyncSessionTest = async_sessionmaker(engine_test)
# user_session = async_sessionmaker(engine_test)


@pytest.fixture(scope="session", autouse=True)
async def setup_db():

    async with engine_db.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield 

    async with engine_db.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(scope="function", autouse=True)
def override_get_async_session():
    async def _get_test_session():
        async with AsyncSessionTest() as session:
            yield session

    app.dependency_overrides[get_async_session] = _get_test_session
    return _get_test_session

#   Создание нужно будет сюда перенести, чтобы не создавать в каждом тестовом файле пользователей (тесты товаров будут в другом файле, а создание юзеров происходит только в test_auth)

@pytest.fixture
async def user_manager(override_get_async_session):
    """Создает экземпляр UserManager для использования в тестах."""
    # Получаем сессию из override_get_async_session
    async for session in override_get_async_session():
        user_db = SQLAlchemyUserDatabase(session, User)  # Создаём SQLAlchemyUserDatabase
        return UserManager(user_db=user_db)

from fastapi_users.password import PasswordHelper
password = PasswordHelper()

@pytest.fixture()
async def test_user(override_get_async_session):
    hashed = password.hash("Bb3##")
    async for session in override_get_async_session():
        user = [
            User(
                username='testver',
                email="ver@gmail.com",
                hashed_password=hashed,
                role='seller',
                is_active=True,
                is_superuser=False,
                is_verified=False
            ),
            User(
                username='testver2',
                email="ver2@gmail.com",
                hashed_password=hashed,
                role='seller',
                is_active=True,
                is_superuser=False,
                is_verified=False
            )
        ]


        
        session.add_all(user)
        await session.commit()


    
