from fastapi import FastAPI

from auth.base_config import fastapi_users, auth_backend
from auth.router import router_reg, router_user


app = FastAPI(
    title="E-commerce prog"
)

# authentication router
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    #prefix="/auth",
    tags=["Authentification"],
)

# Registration router
app.include_router(router_reg)

# users operations
app.include_router(router_user)
