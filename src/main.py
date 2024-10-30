from fastapi import FastAPI

from auth.base_config import fastapi_users, auth_backend
from auth.schemas import UserCreate, UserRead


app = FastAPI(
    title="E-commerce prog"
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)