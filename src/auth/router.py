from fastapi import APIRouter, Depends, HTTPException
from fastapi_users.exceptions import UserAlreadyExists, UserNotExists

from auth.schemas import UserCreate, UserRead, UserReg, UserInfo, MyInfo
from auth.base_config import fastapi_users
from auth.manager import UserManager
from tasks.email_msg import verify_account


router_reg = APIRouter(
    #prefix="register",
    tags=["Registration"]
)

router_user = APIRouter(
    tags=["Users"]
)

# удаление юзеров и становление админом
# router_admin

@router_reg.post("/register")
async def custom_registration(
    data: UserReg,
    user_manager: UserManager = Depends(fastapi_users.get_user_manager)
) -> str:

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
        await user_manager.create(user)
        return f"Registration was successfull"
    except UserAlreadyExists:
        raise HTTPException(
            status_code=456,
            detail=f"Email address already registered {user.email}"
        )

@router_user.get("/users/{user_id}", response_model=UserInfo)
async def get_user_by_id(
    value_id: int,
    user_manager: UserManager = Depends(fastapi_users.get_user_manager)
) -> UserInfo:
    try:
        user = await user_manager.get(value_id)
    except UserNotExists:
        raise HTTPException(
            status_code=404, 
            detail="User not found"
        )
    return user

@router_user.get("/me", response_model=MyInfo)
async def get_my_info(
    user = Depends(fastapi_users.current_user()),
    user_manager: UserManager = Depends(fastapi_users.get_user_manager)
) -> MyInfo:
    return await user_manager.get(user.id)

@router_user.post("/me/verified")
async def verify_request(
    user = Depends(fastapi_users.current_user()),
    user_manager: UserManager = Depends(fastapi_users.get_user_manager)
) -> str:
    await user_manager.request_verify(user)
    return f"Email message for verifying was sent"

@router_user.get("/verify/{token}")
async def verify_user(
    token: str,
    user_manager: UserManager = Depends(fastapi_users.get_user_manager)
) -> str:
    verified_user = await user_manager.verify(token)
    return f"Account was verified"