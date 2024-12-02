import pytest
from contextlib import nullcontext as not_raise

from httpx import ASGITransport, AsyncClient
from fastapi_users.jwt import generate_jwt

from main import app
from auth.manager import UserManager
from auth.models import User


class TestAuth:

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "payload, status, exception",
        [
            (
                {
                    "user_name": "test_seller",
                    "user_email": "test_user@gmail.com",
                    "user_password": "Aa2@@",
                    "user_role": "seller"
                }, 
                200, 
                f"Registration was successfull"
            ),
            (
                {
                    "user_name": "test_customer",
                    "user_email": "test_customer@gmail.com",
                    "user_password": "Aa2@@",
                    "user_role": "customer"
                }, 
                200, 
                f"Registration was successfull"
            ),
            (
                {
                    "user_name": "test_act",
                    "user_email": "test_act@gmail.com",
                    "user_password": "Aa2@@",
                    "user_role": "customer"
                }, 
                200, 
                f"Registration was successfull"
            ),
            (
                {
                    "user_name": "test_user",
                    "user_email": "test_user@ex.com",
                    "user_password": "Aa2@@",
                    "user_role": "seller"
                }, 
                422, 
                f"Value error, Email domain in test_user@ex.com is not validate",
            ),
            (
                {
                    "user_name": "test_user",
                    "user_email": "test_user@gmail.com",
                    "user_password": "A2@@",
                    "user_role": "seller"
                }, 
                422, 
                f"Value error, Password must contain from 5 to 10 symbols",
            ),
            (
                {
                    "user_name": "test_user",
                    "user_email": "test_user@gmail.com",
                    "user_password": "aa2@@",
                    "user_role": "seller"
                }, 
                422, 
                f"Value error, Password must contain at least one uppercase letter",
            ),
            (
                {
                    "user_name": "test_user",
                    "user_email": "test_user@gmail.com",
                    "user_password": "AA2@@",
                    "user_role": "seller"
                }, 
                422, 
                f"Value error, Password must contain at least one lowercase letter",
            ),
            (
                {
                    "user_name": "test_user",
                    "user_email": "test_user@gmail.com",
                    "user_password": "Aaa@@",
                    "user_role": "seller"
                }, 
                422, 
                f"Value error, Password must contain at least one digit",
            ),
            (
                {
                    "user_name": "test_user",
                    "user_email": "test_user@gmail.com",
                    "user_password": "Aa222",
                    "user_role": "seller"
                }, 
                422, 
                f"Value error, Password must contain at least one special character",
            ),
            (
                {
                    "user_name": "test_user",
                    "user_email": "test_user@gmail.com",
                    "user_password": "Aa2@@",
                    "user_role": "customer"
                },
                456,
                f"Email address already registered test_user@gmail.com"
            )            
        ]
    )
    async def test_registration(self, payload, status, exception):
        
        async with AsyncClient(
            transport=ASGITransport(app=app), 
            base_url="http://test"
        ) as client:

            response = await client.post("/register", json=payload)

        assert response.status_code == status
        if response.status_code == 422:
            assert response.json()['detail'][0]['msg'] == exception
        elif response.status_code == 456:
            assert response.json()['detail'] == exception
        else:
            assert response.json() == exception

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "payload, status, exception",
        [
            (
                {
                    'email': 'test_user@gmail.com',
                    'password': 'Aa2@@'
                },
                204,
                None
            ),
            (
                {
                    'email': 'test_user@gmail.com',
                    'password': 'A2@@'
                },
                400,
                f"LOGIN_BAD_CREDENTIALS"
            )
        ]
    )
    async def test_login_logout(self, payload, status, exception):

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(f"/login", data=payload)
            
            assert response.status_code == status
            if response.status_code == 204:
                cookie_app = response.cookies.get("e_commerce")
                assert cookie_app is not None

                cookies = {"e_commerce": cookie_app}
                response = await client.post('/logout', cookies=cookies)
                assert response.status_code == 204 and "e_commerce" not in response.cookies

            elif response.status_code == 400:
                assert response.json()['detail'] == exception

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "value, status, exception",
        [
            (
                "1",
                200,
                None
            ),
            (
                "4",
                404,
                f"User not found"
            ),
            (
                "A",
                422,
                f"Input should be a valid integer, unable to parse string as an integer"
            )
        ]
    )
    async def test_get_user(self, value, status, exception):
        
        async with AsyncClient(
            transport=ASGITransport(app=app), 
            base_url="http://test"
        ) as client:
            response = await client.get(f"/users/{value}")

        assert response.status_code == status
        if response.status_code == 422:
            assert response.json()['detail'][0]['msg'] == exception
        elif response.status_code == 404:
            assert response.json()['detail'] == exception
        else:
            user_data = response.json()
            assert 'username' in user_data and 'role' in user_data

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "payload, status",
        [
            (
                {
                    "email": "test_user@gmail.com",
                    "password": "Aa2@@",
                }, 
                204
            ),
            (
                {
                    "email": "test_customer@gmail.com",
                    "password": "Aa2@@",
                }, 
                204
            ),
            (
                {
                    "email": "test_cu1stomer@gmail.com",
                    "password": "Aa2@@",
                }, 
                400
            )
        ]
    )
    async def test_about_me(self, payload, status):

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(f'/login', data=payload)
            
            assert response.status_code == status
            
            if response.status_code == 204:
                cookie_app = response.cookies.get('e_commerce')
                cookies = {"e_commerce": cookie_app}
                response = await client.get(f'/about_me', cookies=cookies)
                
                assert response.status_code == 200 and 'email' in response.json()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "payload, status, exception",
        [
            (
                {
                    "email": "test_act@gmail.com",
                    "password": "Aa2@@",
                }, 
                200,
                f"User with id = 3 is admin"
            ),
            (
                {
                    "email": "test_act@gmail.com",
                    "password": "Aa2@@",
                }, 
                470,
                f"User is already admin"
            )
        ]
    )
    async def test_admin(self, payload, status, exception):

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            
            response = await client.post(f'/login', data=payload)
            
            cookie_app = response.cookies.get('e_commerce')
            cookies = {"e_commerce": cookie_app}
            
            response = await client.patch(f'/control/admin', cookies=cookies)

            assert response.status_code == status
            if response.status_code == 470:
                assert response.json()['detail'] == exception

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "payload, status, exception, status_not, exp_not, status_already, exp_already",
        [
            (
                {
                    "email": "test_user@gmail.com",
                    "password": "Aa2@@",
                }, 
                470, 
                f"User is not admin",
                None,
                None,
                None,
                None
            ),
            (
                {
                    "email": "test_act@gmail.com",
                    "password": "Aa2@@",
                }, 
                200, 
                None,
                471,
                f"User is not found",
                472,
                f"User is already deactivate"
            )
        ]
    )
    async def test_deactivate_user(self, payload, status, exception, 
                                   status_not, exp_not, status_already, exp_already):

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            
            response = await client.post('/login', data=payload)

            cookie_app = response.cookies.get('e_commerce')
            cookies = {'e_commerce': cookie_app}
            assert response.status_code == 204

            response = await client.patch('/control/deactivate', params={'id': 2}, cookies=cookies)
            
            assert response.status_code == status
            if response.status_code != 470:
                response = await client.patch('/control/deactivate', 
                                              params={'id': 2}, cookies=cookies)
                assert response.status_code == status_already and \
                    response.json()['detail'] == exp_already
                
                response = await client.patch('/control/deactivate', 
                                              params={'id': 999}, cookies=cookies)
                assert response.status_code == status_not and \
                    response.json()['detail'] == exp_not
            else:
                assert response.json()['detail'] == exception

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "payload, status, exception, status_not, exp_not, status_already, exp_already",
        [
            (
                {
                    "email": "test_user@gmail.com",
                    "password": "Aa2@@",
                }, 
                470, 
                f"User is not admin",
                None,
                None,
                None,
                None
            ),
            (
                {
                    "email": "test_act@gmail.com",
                    "password": "Aa2@@",
                }, 
                200, 
                None,
                471,
                f"User is not found",
                472,
                f"User is already activate"
            )
        ]
    )
    async def test_activate_user(self, payload, status, exception, 
                                 status_not, exp_not, status_already, exp_already):

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            
            response = await client.post('/login', data=payload)

            cookie_app = response.cookies.get('e_commerce')
            cookies = {'e_commerce': cookie_app}
            assert response.status_code == 204
        
            response = await client.patch('/control/activate', params={'id': 2}, cookies=cookies)
            
            assert response.status_code == status
            if response.status_code != 470:
                response = await client.patch('/control/activate', 
                                              params={'id': 2}, cookies=cookies)
                assert response.status_code == status_already and \
                    response.json()['detail'] == exp_already
                
                response = await client.patch('/control/activate', 
                                              params={'id': 999}, cookies=cookies)
                assert response.status_code == status_not and \
                    response.json()['detail'] == exp_not

            else:
                assert response.json()['detail'] == exception

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "payload, status, exception, status_not, exp_not, status_yourself, exp_yourself",
        [
            (
                {
                    "email": "test_user@gmail.com",
                    "password": "Aa2@@",
                }, 
                470, 
                f"User is not admin",
                None,
                None,
                None,
                None
            ),
            (
                {
                    "email": "test_act@gmail.com",
                    "password": "Aa2@@",
                }, 
                200, 
                f"User with id = 1 was deleted",
                471,
                f"User is not found",
                472,
                f"U dont delete yourself"
            )
        ]
    )
    async def test_delete_user(self, payload, status, exception, 
                               status_not, exp_not, status_yourself, exp_yourself):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:

            response = await client.post('/login', data=payload)

            cookie_app = response.cookies.get('e_commerce')
            cookies = {'e_commerce': cookie_app}
            assert response.status_code == 204
        
            response = await client.delete(f'/control/delete', params={'id': 1}, cookies=cookies)
            
            assert response.status_code == status
            if response.status_code != 470:
                response = await client.delete('/control/delete', 
                                               params={'id': 1}, cookies=cookies)
                assert response.status_code == status_not and \
                    response.json()['detail'] == exp_not
                response = await client.delete('/control/delete', 
                                               params={'id': 3}, cookies=cookies)
                assert response.status_code == status_yourself and \
                    response.json()['detail'] == exp_yourself
            else:
                assert response.json()['detail'] == exception

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "payload, status, exception",
        [
            (
                {
                    'id': '3',
                    'email': 'test_act@gmail.com'
                },
                200,
                f"Account was verified. U can close the tab"
            ),
            (
                {
                    'id': '3',
                    'email': '1_act@gmail.com'
                },
                413,
                f"User not exists"
            )
        ]
    )
    async def test_verify_user(sefl, user_manager, payload, status, exception):
        async with AsyncClient(
            transport=ASGITransport(app=app), 
            base_url="http://test"
        ) as client:
            token = generate_jwt(
                {
                    "sub": payload['id'],
                    "email": payload['email'],
                    "aud": user_manager.verification_token_audience,
                },
                user_manager.verification_token_secret,
                user_manager.verification_token_lifetime_seconds,
            )

            response = await client.post(f"/options/verify/{1}")
            assert response.status_code == 412
            response = await client.post(f"/options/verify/{token}")
            assert response.status_code == status
            if response.status_code == 200:
                assert response.json() == exception
                response = await client.post(f"/options/verify/{token}")
                assert response.status_code == 416
                assert response.json()['detail'] == f"User already verified"
            else:
                assert response.json()['detail'] == exception
