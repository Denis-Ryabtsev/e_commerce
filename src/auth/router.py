from fastapi import APIRouter, Depends, HTTPException
from fastapi_users.exceptions import UserAlreadyExists
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas import UserCreate, UserRead, email_domain
from auth.base_config import fastapi_users
from auth.manager import UserManager
from database import get_async_session


router_reg = APIRouter(
    #prefix="register",
    tags=["Registration"]
)

@router_reg.post("/register", response_model=UserRead)
async def custom_reg(
        user: UserCreate, 
        user_manager: UserManager = Depends(fastapi_users.get_user_manager)
    ) -> UserRead:

    domain = user.email[user.email.find("@"):]
    if domain not in email_domain:
        raise HTTPException(
            status_code=444,
            detail=f"Email domain {domain} is not validate"
        )
    try:
        return await user_manager.create(user)
    except UserAlreadyExists:
        raise HTTPException(
            status_code=456,
            detail=f"Email address already registered {user.email}"
        )