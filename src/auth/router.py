from fastapi import APIRouter, Depends, HTTPException
from fastapi_users.exceptions import UserAlreadyExists

from auth.schemas import UserCreate, UserRead, UserReg
from auth.base_config import fastapi_users
from auth.manager import UserManager
from auth.check_param import validate_email, validate_pass


router_reg = APIRouter(
    #prefix="register",
    tags=["Registration"]
)

@router_reg.post("/register", response_model=UserRead)
async def custom_registration(
        data: UserReg,
        user_manager: UserManager = Depends(fastapi_users.get_user_manager)
    ) -> UserRead:

    if not(validate_email(data.user_email)):
        raise HTTPException(
            status_code=444,
            detail=f"Email domain in {data.user_email} is not validate"
        )
    elif not(validate_pass(data.user_password)):
        raise HTTPException(
            status_code=445,
            detail=f"Password is not validate! (check password requirements)"
        )
    try:
        user = UserCreate(
            username=data.user_name,
            email=data.user_email,
            password=data.user_password,
            role=data.user_role,
            is_active=True,
            is_superuser=False,
            is_verified=False
        )
        return await user_manager.create(user)
    except UserAlreadyExists:
        raise HTTPException(
            status_code=456,
            detail=f"Email address already registered {user.email}"
        )