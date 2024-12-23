from fastapi_users.authentication import AuthenticationBackend, \
                                            CookieTransport, \
                                            JWTStrategy
from fastapi_users import FastAPIUsers

from config import setting
from auth.manager import get_user_manager
from auth.models import User


cookie_transport = CookieTransport(
    cookie_name="e_commerce",
    cookie_max_age=3600
    )

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=setting.SECRET_AUTH, 
        lifetime_seconds=3600
    )

auth_backend = AuthenticationBackend(
        name="jwt",
        transport=cookie_transport,
        get_strategy=get_jwt_strategy,
    )

fastapi_users = FastAPIUsers[User, int](
        get_user_manager,
        [auth_backend],
    )