import enum
from datetime import datetime

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, String, TIMESTAMP, Enum

from database import Base


class RoleType(enum.Enum):
    customer = "customer"
    seller = "seller"


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

    # good
    goods = relationship(
        'Good', 
        back_populates='users'
    )
    # orders
    ord_sel = relationship(
        'Order', 
        foreign_keys='[Order.seller_id]', 
        back_populates='seller'
    )
    ord_cus = relationship(
        'Order',
        foreign_keys='[Order.customer_id]',
        back_populates='customer'
    )