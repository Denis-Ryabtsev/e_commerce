import enum
from datetime import datetime

from fastapi_users.db import SQLAlchemyBaseUserTable, \
                                SQLAlchemyUserDatabase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Boolean, ForeignKey, String, TIMESTAMP, Enum, JSON

from database import Base


class RoleType(enum.Enum):
    customer = "customer"
    serller = "seller"


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )
    username: Mapped[str] = mapped_column(
        String(length=320), nullable=False
    )
    role: Mapped[RoleType] = mapped_column(
        Enum(RoleType), nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, nullable=False
    )
    registry_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.now()
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )