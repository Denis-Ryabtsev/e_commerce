from pydantic import BaseModel

from management.models import CategoryType


class AddGood(BaseModel):
    good_name: str
    good_category: CategoryType
    good_price: float


class GoodSeller(BaseModel):
    seller_name: str
    good_name: str
    good_category: CategoryType
    good_price: float


class MyOrder(BaseModel):
    id: int
    description: str