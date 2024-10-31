from fastapi import FastAPI

from auth.base_config import fastapi_users, auth_backend
from auth.schemas import UserCreate, UserRead
from auth.router import router_reg
from database import get_async_session


app = FastAPI(
    title="E-commerce prog"
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    #prefix="/auth",
    tags=["Authentification"],
)


app.include_router(router_reg)