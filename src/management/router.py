from typing import Union, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, insert, select, func, update

from tasks.email_msg import customer_order, seller_order
from management.schemas import AddGood, GoodSeller, MyOrder
from management.models import Good, Category, CategoryType, Order, OrderDetail
from auth.base_config import fastapi_users
from auth.models import User, RoleType
from database import get_async_session


# декоратор для проверки роли пользователя и верификации при выставлении товара
# проверка: является ли пользователь с указанным ИД продажником или нет

router_good = APIRouter(
    prefix='/goods',
    tags=['Goods operations']
)

router_order = APIRouter(
    prefix='/orders',
    tags=['Orders operations']
)

@router_good.post('/add', response_model=Optional[str])
async def add_good(
    data: AddGood,
    user = Depends(fastapi_users.current_user()),
    session: AsyncSession = Depends(get_async_session)
) -> Union[str, HTTPException]:
    
    if user.role != RoleType.seller:
        raise HTTPException(
            status_code=400,
            detail=f"Operations with goods only for sellers!"
        )
    elif not user.is_verified:
        raise HTTPException(
            status_code=400,
            detail=f"Seller is not verified!"
        )
    user_id = user.id

    query = \
        select(
            Category.id
        ).filter(
            Category.category_name == data.good_category
        )
    
    try:    
        cat_id = (await session.execute(query)).first()
        product = {
            "product_name": data.good_name,
            "seller_id": user_id,
            "category_id": cat_id.id,
            "unit_price": data.good_price
        }
        # session.add(product)
        stmt = \
            insert(
                Good
            ).values(product)
        
        await session.execute(stmt)
        await session.commit()
        return f"Good {product['product_name']} was added"
    except Exception as e:
        raise HTTPException(
            status_code=501,
            detail=str(e)
        )

@router_good.get('/my_goods', response_model=Union[list[AddGood], str])
async def get_goods(
    user = Depends(fastapi_users.current_user()),
    session: AsyncSession = Depends(get_async_session)
) -> Union[list[AddGood], str]:
    
    query = \
        select(
            Good.product_name,
            Category.category_name,
            Good.unit_price
        ).join(
            Good, Good.category_id == Category.id
        ).group_by(
            Good.product_name,
            Category.category_name,
            Good.unit_price
        ).filter(
            Good.seller_id == user.id
        )
    
    temp = (await session.execute(query)).all()
    result = [
        AddGood(
            good_name=item.product_name,
            good_category=item.category_name,
            good_price=item.unit_price
        )
        for item in temp
    ]
    
    return result if result else f"Nothing"

@router_good.get('/seller/{id}', response_model=Union[list[AddGood], str])
async def goods_seller(
    id: int,
    session: AsyncSession = Depends(get_async_session)
) -> Union[list[AddGood], str]:
    
    query = \
        select(
            User.username,
            Good.product_name,
            Category.category_name,
            Good.unit_price
        ).join(
            Good, Good.category_id == Category.id
        ).join(
            User, User.id == Good.seller_id
        ).group_by(
            User.username,
            Good.product_name,
            Category.category_name,
            Good.unit_price
        ).filter(
            Good.seller_id == id
        )
    
    temp = (await session.execute(query)).all()
    result = [
        GoodSeller(
            seller_name=item.username,
            good_name=item.product_name,
            good_category=item.category_name,
            good_price=item.unit_price
        )
        for item in temp
    ]
    
    return result if result else f"This seller without goods!"

async def get_max_price(
    category: Optional[CategoryType] = None,
    session: AsyncSession = Depends(get_async_session)
) -> Optional[float]:
    
    if not category:
        query_price = \
            select(
                func.max(Good.unit_price).label('max_price')
            )
    else:
        query_id = \
            select(
                Category.id
            ).filter(
                Category.category_name == category
            )

        cat_id = (await session.execute(query_id)).first()
        
        query_price = \
            select(
                func.max(Good.unit_price).label('max_price')
            ).filter(
                Good.category_id == cat_id.id
            )
        
    temp = (await session.execute(query_price)).first()
    return temp.max_price

@router_good.get('/search', response_model=Union[list[GoodSeller], None, str])
async def find_by_filter(
    category: Optional[CategoryType] = None,
    min_price: Optional[float] = 0,
    max_price: Optional[float] = None,
    session: AsyncSession = Depends(get_async_session)
) -> Union[list[GoodSeller], None, str]:
    
    if not max_price:
        try:
            max_price = await get_max_price(category, session)
        except Exception:
            raise HTTPException(
                status_code=550,
                detail=f"Goods are not exists"
            )

    if category:
        query = \
            select(
                Good.product_name,
                User.username,
                Category.category_name,
                Good.unit_price   
            ).join(
                Good, Good.seller_id == User.id
            ).join(
                Category, Category.id == Good.category_id
            ).filter(
                Good.unit_price.between(min_price, max_price),
                Category.category_name == category
            ).group_by(
                Good.product_name,
                User.username,
                Category.category_name,
                Good.unit_price  
            )
    else:
        query = \
            select(
                Good.product_name,
                User.username,
                Category.category_name,
                Good.unit_price   
            ).join(
                Good, Good.seller_id == User.id
            ).join(
                Category, Category.id == Good.category_id
            ).filter(
                Good.unit_price.between(min_price, max_price)
            ).group_by(
                Good.product_name,
                User.username,
                Category.category_name,
                Good.unit_price  
            )
    
    temp = (await session.execute(query)).all()
    result = [
        GoodSeller(
            seller_name=item.username,
            good_name=item.product_name,
            good_category=item.category_name,
            good_price=item.unit_price
        )
        for item in temp
    ]

    return result if result else f"Goods to params are not found"

@router_good.patch('/change_price', response_model=str)
async def change_price(
    id: int,
    price: float,
    session: AsyncSession = Depends(get_async_session)
) -> str:
    
    stmt = \
        update(
            Good
        ).filter(
            Good.id == id
        ).values(
            unit_price = price
        )
    
    await session.execute(stmt)
    await session.commit()

    return f"Price of good #{id} was changed"

@router_good.delete('/delete', response_model=Optional[str])
async def delete_good(
    good_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> Union[str, HTTPException]:
    
    try:
        query = \
            select(
                Good.product_name
            ).filter(
                Good.id == good_id
            )

        stmt = \
            delete(
                Good
            ).filter(
                Good.id == good_id
            )
        
        name = (await session.execute(query)).first()
        await session.execute(stmt)
        await session.commit()
        
        return f"Good '{name.product_name}' was deleted with market"
    except Exception as error:
        raise HTTPException(
            status_code=555,
            detail=str(error)
        )

@router_order.post('/add', response_model=Optional[str])
async def add_orders(
    product_list: list[int],
    count_list: list[int],
    country: str,
    session: AsyncSession = Depends(get_async_session),
    user = Depends(fastapi_users.current_user())
) -> Union[str, HTTPException]:
    
    if not user.is_verified:
        raise HTTPException(
            status_code=400,
            detail=f"Customers is not verified!"
        )

    user_id = user.id
    stmt = insert(Order).values(
        customer_id=user_id,
        ship_country=country
    )
    query = \
        select(
            Good.unit_price
        ).filter(
            Good.id.in_(product_list)
        )
    
    ord_id = (await session.execute(stmt)).inserted_primary_key[0]
    await session.commit()
    prices = (await session.execute(query)).scalars().all()

    data = [
        {
            "order_id": ord_id,
            "good_id": product_list[item],
            "quantity": count_list[item],
            "price": prices[item] * count_list[item]
        }
        for item in range(len(prices)) 
    ]

    stmt = \
        insert(
            OrderDetail
        ).values(
            data
        )
    
    await session.execute(stmt)
    await session.commit()

    items_list = []
    for item in data:
        query = \
            select(
                User.email,
                Good.product_name,
                OrderDetail.quantity
            ).join(
                Good, Good.id == OrderDetail.good_id
            ).join(
                User, User.id == Good.seller_id
            ).filter(
                Good.id == item['good_id']
            )
        
        items_list.append((await session.execute(query)).first())
    
    email_query = \
        select(
            User.email
        ).filter(
            User.id == user_id
        )
    
    customer_email = (await session.execute(email_query)).first()

    seller_order(items_list)
    customer_order(items_list, customer_email.email)

    return f"Ur order was created. U get a message with details of order"

@router_order.delete('/delete', response_model=Optional[str])
async def delete_order(
    id: int,
    session: AsyncSession = Depends(get_async_session)
) -> Union[str, HTTPException]:

    query = \
        select(
            Order
        ).filter(
            Order.id == id
        )
    temp = (await session.execute(query)).first()
    if not temp:
        raise HTTPException(
            status_code=487,
            detail=f"Order with this number doesnt exist"
        )

    stmt = \
        delete(
            Order
        ).filter(
            Order.id == id
        )

    await session.execute(stmt)
    await session.commit()

    return f"Order #{id} was deleted"

@router_order.get('/my_orders',response_model=Optional[list[MyOrder]])
async def get_orders(
    user = Depends(fastapi_users.current_user()),
    session: AsyncSession = Depends(get_async_session)
) -> Union[MyOrder, HTTPException]:
    user_id = user.id

    query = \
        select(
            Order.id,
            Good.product_name,
            Good.unit_price,
            OrderDetail.quantity,
            Order.ship_country
        ).join(
            OrderDetail, OrderDetail.good_id == Good.id
        ).join(
            Order, Order.id == OrderDetail.order_id
        ).filter(
            Order.customer_id == user_id
        ).group_by(
            Order.id,
            Good.product_name,
            Good.unit_price,
            OrderDetail.quantity,
            Order.ship_country
        )
    
    result = (await session.execute(query)).all()
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Orders not found"
        )

    data = {}
    list_orders = []

    for item in result:
        if item.id not in data:
            data[item.id] = []
        data[item.id].append((
            item.product_name, item.unit_price, item.quantity, item.ship_country
        ))
    for numb, temp in data.items():
        obj = "| ".join([f"|Good: {good}, price: {price}, "\
                         f"count: {count}, country: {country}" \
                         for good, price, count, country in temp])
        list_orders.append((numb, str(obj)))
    
    result = [
        MyOrder(
            id=item[0],
            description=item[1]
        )
        for item in list_orders
    ]

    return result

