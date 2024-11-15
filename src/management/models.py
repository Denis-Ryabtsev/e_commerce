from datetime import datetime
import enum

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import TIMESTAMP, ForeignKey, Enum

from database import Base


class CategoryType(enum.Enum):
    beverages = 'beverages'
    confections = 'confections'
    cars = 'cars'
    games = 'games'


class Good(Base):
    __tablename__ = 'good'

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )
    product_name: Mapped[str] = mapped_column(
        nullable=False
    )
    seller_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE')
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey('category.id')
    )
    unit_price: Mapped[float] = mapped_column(
        nullable=False
    )

    users = relationship(
        'User', 
        back_populates='goods'
    )
    categories = relationship(
        'Category', 
        back_populates='goods'
    )
    od = relationship(
        'OrderDetail',
        back_populates='goods'
    )

class Order(Base):
    __tablename__ = 'order'

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete='CASCADE')
    )
    date_order: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.now()
    )
    ship_country: Mapped[str] = mapped_column(
        nullable=False
    )

    customer = relationship(
        'User', 
        foreign_keys=[customer_id], 
        back_populates='ord_cus'
    )

    od = relationship(
        'OrderDetail',
        back_populates='orders',
        cascade="all, delete"
    )


class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )
    category_name: Mapped[CategoryType] = mapped_column(
        Enum(CategoryType), nullable=False
    )
    description: Mapped[str]

    goods = relationship(
        'Good', 
        back_populates='categories'
    )


class OrderDetail(Base):
    __tablename__ = 'order_detail'

    order_id: Mapped[int] = mapped_column(
        ForeignKey('order.id', ondelete='CASCADE'), primary_key=True
    )
    good_id: Mapped[int] = mapped_column(
        ForeignKey('good.id', ondelete='CASCADE'), primary_key=True
    )
    quantity: Mapped[int] = mapped_column(
        nullable=False
    )
    price: Mapped[float] = mapped_column(
        nullable=False
    )

    orders = relationship(
        'Order',
        back_populates='od'
    )
    goods = relationship(
        'Good',
        back_populates='od'
    )