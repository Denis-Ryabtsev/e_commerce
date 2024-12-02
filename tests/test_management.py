import pytest

from httpx import ASGITransport, AsyncClient

from main import app
from management.schemas import AddGood


class TestManagement:

    #   create users by fixture
    @pytest.mark.asyncio
    async def test_create_users(self, test_user):
        pass

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "data_user, data_good, status, exception",

        [
            (
                {
                    'email': 'custver@gmail.com',
                    'password': 'Bb3##'
                },
                {
                    "good_name": 'rx8',
                    "good_category": 'cars',
                    "good_price": 20,
                },
                491,
                f"Operations with goods only for sellers!"
            ),
            (
                {
                    'email': 'sellver@gmail.com',
                    'password': 'Bb2@@'
                },
                {
                    "good_name": 'rx8',
                    "good_category": 'cars',
                    "good_price": 20,
                },
                200,
                f"Good rx8 was added"

            ),
            (
                {
                    'email': 'sellver@gmail.com',
                    'password': 'Bb2@@'
                },
                {
                    "good_name": 'rx7',
                    "good_category": 'cars',
                    "good_price": 32.5,
                },
                200,
                f"Good rx7 was added"
            ),
            (
                {
                    'email': 'sellver@gmail.com',
                    'password': 'Bb2@@'
                },
                {
                    "good_name": 'pubg',
                    "good_category": 'games',
                    "good_price": 3.8,
                },
                200,
                f"Good pubg was added"

            ),
            (
                {
                    'email': 'sellnot@gmail.com',
                    'password': 'Bb4$$'
                },
                {
                    "good_name": 'rx8',
                    "good_category": 'cars',
                    "good_price": 20,
                },
                492,
                f"Seller is not verified!"

            )
        ]
    )
    async def test_add_good(self, data_user, data_good, status, exception):

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            
            response = await client.post(f"/login", data=data_user)
            assert response.status_code == 204
            cookie_app = {'e_commerce': response.cookies.get('e_commerce')}

            response = await client.post(f"/goods/add", json=data_good, cookies=cookie_app)
            assert response.status_code == status
            if response.status_code == 200:
                assert response.json() == exception
            else:
                assert response.json()['detail'] == exception
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "data_user, status, exception",

        [
            (
                {
                    'email': 'sellver@gmail.com',
                    'password': 'Bb2@@'
                },
                200,
                ["rx8", "rx7", "pubg"]

            ),
            (
                {
                    'email': 'sellnot@gmail.com',
                    'password': 'Bb4$$'
                },
                200,
                f"Nothing"

            )
        ]
    )
    async def test_get_goods(self, data_user, status, exception):

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            
            response = await client.post(f"/login", data=data_user)
            assert response.status_code == 204
            cookie_app = {'e_commerce': response.cookies.get('e_commerce')}

            response = await client.get(f"/goods/my_goods", cookies=cookie_app)
            assert response.status_code == status
            if response.json() != f'Nothing':
                assert (item['good_name'] in exception for item in response.json())

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "seller_id, exception",
        [
            (
                6,
                f"sellver"
            ),
            (
                7,
                f"This seller without goods!"
            )
        ]
    )
    async def test_goods_seller(self, seller_id, exception):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            
            response = await client.get(f"/goods/seller/{seller_id}")

            if not isinstance(response.json(), str):
                assert any([item['seller_name'] == exception for item in response.json()])
            else:
                assert response.json() == exception 

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "category, min_coast, max_coast, status, exception",
        [
            (
                'cars',
                25,
                None,
                200,
                f"rx7"
            ),
            (
                'cars',
                None,
                27,
                200,
                f"rx8"
            ),
            (
                None,
                None,
                None,
                200,
                3
            ),
            (
                'beverages',
                None,
                None,
                200,
                f"Goods to params are not found"
            ),
        ]
    )
    async def test_find_by_filter(self, category, min_coast, max_coast, status, exception):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            
            temp = {
                'category': category,
                'min_price': min_coast,
                'max_price': max_coast
            }
            data = {
                key: value for key, value in temp.items() if value
            }
            
            response = await client.get(f"/goods/search", params=data)
            assert response.status_code == status

            if isinstance(response.json(), str):
                assert response.json() == exception
            elif len(response.json()) == 1:
                assert response.json()[0]['good_name'] == exception
            else:
                assert len(response.json()) == exception

    @pytest.mark.asyncio 
    @pytest.mark.parametrize(
        "good_id, price",
        [
            (
                1,
                23.7
            ),
            (
                2,
                41.7
            )
        ]
    )
    async def test_change_price(self, good_id, price):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            
            values = {
                'id': good_id,
                'price': price 
            }

            response = await client.patch("/goods/change_price", params=values)
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "good_id, status, exception",
        [
            (
                3,
                200,
                f"Good 'pubg' was deleted with market"
            ),
            (
                73,
                555,
                f"'NoneType' object has no attribute 'product_name'"
            ),
        ]
    )
    async def test_delete_good(self, good_id, status, exception):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            
            response = await client.delete(f"goods/delete", params={'good_id': good_id})
            assert response.status_code == status
            if response.status_code == 200:
                assert response.json() == exception
            else:
                assert response.json()['detail'] == exception

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "products, count, country, payload, status, exception",
        [
            (
                [1, 2],
                [4, 5],
                f'Moscow',
                {
                    'email': 'custver@gmail.com',
                    'password': 'Bb3##'
                },
                200,
                f"Ur order was created. U get a message with details of order"
            ),
            (
                [1],
                [10],
                f'Baku',
                {
                    'email': 'custver@gmail.com',
                    'password': 'Bb3##'
                },
                200,
                f"Ur order was created. U get a message with details of order"
            )
        ]
    )
    async def test_add_orders(self, products, count, country, payload, status, exception):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            
            response = await client.post(f'/login', data=payload)
            cookie_app = {'e_commerce': response.cookies.get('e_commerce')}
            
            values = {
                'product_list': products,
                'count_list': count,
                'country': country
            }

            response = await client.post(f'/orders/add', cookies=cookie_app, json=values)
            
            assert response.status_code == status and response.json() == exception

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "payload, status, exception",
        [
            (
                {
                    'email': 'custver@gmail.com',
                    'password': 'Bb3##'
                },
                200,
                None
            ),
            (
                {
                    'email': 'custnot@gmail.com',
                    'password': 'Bb1!!'
                },
                404,
                f"Orders not found"
            )
        ]
    )
    async def test_get_orders(self, payload, status, exception):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            
            response = await client.post(f'/login', data=payload)
            cookie_app = {'e_commerce': response.cookies.get('e_commerce')}

            response = await client.get(f"/orders/my_orders", cookies=cookie_app)

            assert response.status_code == status
            if response.status_code == 404:
                assert response.json()['detail'] == exception
            else:
                assert isinstance(response.json(), list) and len(response.json()) == 2
                
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "order_id, status, exception",
        [
            (
                3,
                487,
                f"Order with this number doesnt exist"
            ),
            (
                2,
                200,
                f"Order #2 was deleted"
            )
        ]
    )
    async def test_delete_orders(self, order_id, status, exception):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            
            response = await client.delete(f"/orders/delete", params={'id': order_id})

            assert response.status_code == status
            if response.status_code == 487:
                assert response.json()['detail'] == exception
            else:
                assert response.json() == exception
