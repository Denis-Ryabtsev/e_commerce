from typing import Optional, Union
from fastapi import APIRouter, Depends, HTTPException
from fastapi_users.exceptions import UserAlreadyExists, UserNotExists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, update


from auth.schemas import UserCreate, UserReg, UserInfo, MyInfo
from auth.base_config import fastapi_users
from auth.manager import UserManager
from auth.models import User
from database import get_async_session
from tasks.email_msg import after_delete


router_reg = APIRouter(
    tags=["Registration"]
)

router_user = APIRouter(
    tags=["User interface"]
)

router_option = APIRouter(
    prefix="/options",
    tags=["User interface"]
)

router_admin = APIRouter(
    prefix="/control",
    tags=["Admin interface"]
)


@router_reg.post("/register", response_model=Optional[str])
async def custom_registration(
    data: UserReg,
    user_manager: UserManager = Depends(fastapi_users.get_user_manager)
) -> Union[str, Exception]:

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

@router_user.get("/users/{user_id}", response_model=Optional[UserInfo])
async def get_user_by_id(
    user_id: int,
    user_manager: UserManager = Depends(fastapi_users.get_user_manager)
) -> Union[UserInfo, Exception]:
    
    try:
        user = await user_manager.get(user_id)
    except UserNotExists:
        raise HTTPException(
            status_code=404, 
            detail="User not found"
        )
    
    return user

@router_user.get("/about_me", response_model=MyInfo)
async def get_my_info(
    user = Depends(fastapi_users.current_user()),
    user_manager: UserManager = Depends(fastapi_users.get_user_manager)
) -> MyInfo:
    
    return await user_manager.get(user.id)

@router_option.post("/verified")
async def verify_request(
    user = Depends(fastapi_users.current_user()),
    user_manager: UserManager = Depends(fastapi_users.get_user_manager)
) -> str:
    
    await user_manager.request_verify(user)
    return f"Email message for verifying was sent"

@router_option.post("/verify/{token}")
async def verify_user(
    token: str,
    user_manager: UserManager = Depends(fastapi_users.get_user_manager)
) -> str:
    
    await user_manager.verify(token)
    return f"Account was verified. U can close the tab"

@router_option.post("/forgot")
async def forgot_pass(
    user = Depends(fastapi_users.current_user()),
    user_manager: UserManager = Depends(fastapi_users.get_user_manager)
) -> str:
    
    await user_manager.forgot_password(user)
    return f"Message with instruction was sent"

@router_option.post("/reset/{token}")
async def reset_pass(
    token: str,
    passwd: str,
    user_manager: UserManager = Depends(fastapi_users.get_user_manager)
) -> str:
    
    await user_manager.reset_password(token, passwd)
    return f"Password was recovery"

@router_admin.patch("/deactivate", response_model=Optional[str])
async def deactivate_user(
    id: int,
    user = Depends(fastapi_users.current_user()),
    session: AsyncSession = Depends(get_async_session)
) -> Union[str, Exception]:
    
    if not user.is_superuser:
        raise HTTPException(
            status_code=470,
            detail=f"User is not admin"
        )
    
    check_user = \
        select(
            User
        ).filter(
            User.id == id
        )
    target_user = await session.execute(check_user)
    res = target_user.scalars().first()
    
    if not res:
        raise HTTPException(
            status_code=471,
            detail=f"User is not found"
        )
    
    if not res.is_active:
        raise HTTPException(
            status_code=472,
            detail=f"User is already deactivate"
        )
    
    try:    
        stmt = \
            update(
                User
            ).filter(
                User.id == id
            ).values(
                is_active=False
            )
        
        await session.execute(stmt)
        await session.commit()
        return f"User {res.email} was deactivate"
    except Exception as e:
        raise HTTPException(
            status_code=499,
            detail=str(e)
        )

@router_admin.patch("/activate", response_model=Optional[str])
async def activate_user(
    id: int,
    user = Depends(fastapi_users.current_user()),
    session: AsyncSession = Depends(get_async_session)
) -> Union[str, Exception]:
    
    if not user.is_superuser:
        raise HTTPException(
            status_code=470,
            detail=f"User is not admin"
        )
    
    check_user = \
        select(
            User
        ).filter(
            User.id == id
        )
    target_user = await session.execute(check_user)
    res = target_user.scalars().first()
    
    if not res:
        raise HTTPException(
            status_code=471,
            detail=f"User is not found"
        )
    
    if res.is_active:
        raise HTTPException(
            status_code=472,
            detail=f"User is already activate"
        )
    
    try:    
        stmt = \
            update(
                User
            ).filter(
                User.id == id
            ).values(
                is_active=True
            )
        
        await session.execute(stmt)
        await session.commit()
        return f"User {res.email} was deactivate"
    except Exception as e:
        raise HTTPException(
            status_code=499,
            detail=str(e)
        )
    
@router_admin.delete("/delete", response_model=Optional[str])
async def delete_user(
    id: int,
    user = Depends(fastapi_users.current_user()),
    session: AsyncSession = Depends(get_async_session)
) -> Union[str, Exception]:
    
    if not user.is_superuser:
        raise HTTPException(
            status_code=470,
            detail=f"User is not admin"
        )
    
    if user.id == id:
        raise HTTPException(
            status_code=470,
            detail=f"U dont delete yourself"
        )

    check_user = \
        select(
            User
        ).filter(
            User.id == id
        )
    target_user = await session.execute(check_user)
    res = target_user.scalars().first()
    
    if not res:
        raise HTTPException(
            status_code=471,
            detail=f"User is not found"
        )
    
    try:    
        stmt = \
            delete(
                User
            ).filter(
                User.id == id
            )
        
        await session.execute(stmt)
        await session.commit()
        after_delete(res.email, res.username)
        return f"User {res.email} was deleted"
    except Exception as e:
        raise HTTPException(
            status_code=499,
            detail=str(e)
        )