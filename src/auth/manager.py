from typing import Optional, AsyncGenerator
import jwt

from fastapi import Depends, Request, HTTPException
from fastapi_users.exceptions import UserNotExists, InvalidID
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users.jwt import generate_jwt, decode_jwt

from auth.models import User
from auth.utils import get_user_db
from tasks.email_msg import after_reg, after_reset, \
                            reset_pass, verify_account, after_verify
from config import setting


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = setting.SECRET_AUTH
    verification_token_secret = setting.SECRET_AUTH

    async def request_verify(
        self, 
        user: User, 
        request: Optional[Request] = None
    ) -> None:

        if not user.is_active:
            raise HTTPException(
                status_code=410,
                detail=f"User is not active"
            )
        if user.is_verified:
            raise HTTPException(
                status_code=411,
                detail=f"User already verified"
            )

        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "aud": self.verification_token_audience,
        }
        token = generate_jwt(
            token_data,
            self.verification_token_secret,
            self.verification_token_lifetime_seconds,
        )

        link = f"http://localhost:8000/verify/{token}"

        verify_account(user.email, link, user.username)
        await self.on_after_request_verify(user, token, request)

    async def verify(
        self, 
        token: str, 
        request: Optional[Request] = None
    ) -> User:
        
        try:
            data = decode_jwt(
                token,
                self.verification_token_secret,
                [self.verification_token_audience],
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=412,
                detail=f"Invalid verify token"
            )

        try:
            user_id = data["sub"]
            email = data["email"]
        except KeyError:
            raise HTTPException(
                status_code=412,
                detail=f"Invalid verify token"
            )

        try:
            user = await self.get_by_email(email)
        except UserNotExists:
            raise HTTPException(
                status_code=413,
                detail=f"User not exists"
            )

        try:
            parsed_id = self.parse_id(user_id)
        except InvalidID:
            raise HTTPException(
                status_code=414,
                detail=f"ID is invalid"
            )

        if parsed_id != user.id:
            raise HTTPException(
                status_code=415,
                detail=f"Invalid id"
            )

        if user.is_verified:
            raise HTTPException(
                status_code=416,
                detail=f"User already verified"
            )

        verified_user = await self._update(user, {"is_verified": True})

        await self.on_after_verify(verified_user, request)

        return verified_user

    async def forgot_password(
        self, 
        user: User, 
        request: Optional[Request] = None
    ) -> None:

        if not user.is_active:
            raise HTTPException(
                status_code=430,
                detail=f"User is inactive"
            )

        token_data = {
            "sub": str(user.id),
            "password_fgpt": self.password_helper.hash(user.hashed_password),
            "aud": self.reset_password_token_audience,
        }
        token = generate_jwt(
            token_data,
            self.reset_password_token_secret,
            self.reset_password_token_lifetime_seconds,
        )

        link = f"http://localhost:8000/reset/{token}"

        reset_pass(user.email, link, user.username)
        await self.on_after_forgot_password(user, token, request)

    async def reset_password(
        self, 
        token: str, 
        password: str, 
        request: Optional[Request] = None
    ) -> User:
        try:
            data = decode_jwt(
                token,
                self.reset_password_token_secret,
                [self.reset_password_token_audience],
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=412,
                detail=f"Invalid reset password token"
            )

        try:
            user_id = data["sub"]
            password_fingerprint = data["password_fgpt"]
        except KeyError:
            raise HTTPException(
                status_code=412,
                detail=f"Invalid reset password token"
            )

        try:
            parsed_id = self.parse_id(user_id)
        except InvalidID:
            raise HTTPException(
                status_code=412,
                detail=f"Invalid reset password token"
            )
        
        if not user.is_active:
                    raise HTTPException(
                        status_code=430,
                        detail=f"User is inactive"
                    )
        
        user = await self.get(parsed_id)

        valid_password_fingerprint, _ = self.password_helper.verify_and_update(
            user.hashed_password, password_fingerprint
        )
        if not valid_password_fingerprint:
            raise HTTPException(
                status_code=412,
                detail=f"Invalid reset password token"
            )

        updated_user = await self._update(user, {"password": password})
        await self.on_after_reset_password(user, request)

        return updated_user

    async def on_after_register(
        self, 
        user: User, 
        request: Optional[Request] = None
    ) -> None:
        print(f"User {user.id} has registered.")
        after_reg(user.email, user.username)

    async def on_after_forgot_password(
        self, 
        user: User,
        token: str, 
        request: Optional[Request] = None
    ) -> None:
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_reset_password(
        self, 
        user: User, 
        request: Request | None = None
    ) -> None:
        after_reset(user.email, user.username)

    async def on_after_request_verify(
        self, 
        user: User, 
        token: str, 
        request: Optional[Request] = None
    ) -> None:
        print(f"Verification requested for user {user.id}. Verification token: {token}")
    
    async def on_after_verify(
        self, 
        user: User, 
        request: Optional[Request] = None
    ) -> None:
        after_verify(user.email, user.username)


async def get_user_manager(
    user_db: AsyncGenerator = Depends(get_user_db)
) -> AsyncGenerator:
    yield UserManager(user_db)