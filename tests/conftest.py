import asyncio
import pytest

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from fastapi_users.jwt import generate_jwt
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.password import PasswordHelper
from unittest.mock import patch

from database import get_async_session, Base
from config import setting
from auth.models import User
from management.models import Category
from auth.schemas import UserCreate
from auth.manager import UserManager
from main import app


engine_test = create_async_engine(
    url=setting.DB_URL,
    pool_size=10,
    max_overflow=10, 
    echo=False
)

engine_db = create_async_engine(
    url=setting.DB_URL,
    pool_size=10,
    max_overflow=10,  
    echo=False
)

AsyncSessionTest = async_sessionmaker(engine_test)
user_session = async_sessionmaker(engine_test)

password = PasswordHelper()

@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    assert setting.MODE == 'TEST'
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

async def session_user():
    async with user_session() as session:
        yield session

@pytest.fixture(scope="function", autouse=True)
def override_get_async_session():
    async def _get_test_session():
        async with AsyncSessionTest() as session:
            yield session

    app.dependency_overrides[get_async_session] = _get_test_session
    return _get_test_session

@pytest.fixture
async def user_manager(override_get_async_session):
    async for session in override_get_async_session():
        user_db = SQLAlchemyUserDatabase(session, User) 
        return UserManager(user_db=user_db)

@pytest.fixture()
async def test_user():
    async for session in session_user():
        user = [
            User(
                username='custver',
                email="custver@gmail.com",
                hashed_password=password.hash("Bb3##"),
                role='customer',
                is_active=True,
                is_superuser=False,
                is_verified=True
            ),
            User(
                username='custnot',
                email="custnot@gmail.com",
                hashed_password=password.hash("Bb1!!"),
                role='customer',
                is_active=True,
                is_superuser=False,
                is_verified=False
            ),
            User(
                username='sellver',
                email="sellver@gmail.com",
                hashed_password=password.hash("Bb2@@"),
                role='seller',
                is_active=True,
                is_superuser=False,
                is_verified=True
            ),
            User(
                username='sellnot',
                email="sellnot@gmail.com",
                hashed_password=password.hash("Bb4$$"),
                role='seller',
                is_active=True,
                is_superuser=False,
                is_verified=False
            )
        ]

        categories = [
            Category(
                category_name="beverages",
                description="Coffee, teas, beers"
            ),
            Category(
                category_name="confections",
                description="Desserts, candies, and sweet breads"
            ),
            Category(
                category_name="cars",
                description="Japan and American cars"
            ),
            Category(
                category_name="games",
                description="Computer games"
            )
        ]
        
        session.add_all(user + categories)
        await session.commit()

@pytest.fixture()
def fake_send():
    with patch('tasks.email_msg.send_email.delay') as mocked_send_email:
        yield mocked_send_email

@pytest.fixture()
def fake_smtp():
    with patch('tasks.email_msg.smtplib.SMTP_SSL') as mocked_smtp:
        yield mocked_smtp