import pytest

from httpx import AsyncClient
from tests.conftest import app


@pytest.mark.asyncio(loop_scope="session")
async def test_register():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/auth/register",
            json={
                "email": "test@te.st",
                "password": "test0123",
                "is_active": True,
                "is_superuser": False,
                "is_verified": False,
                "username": "tester",
                "telegram_username": "tg_tester",
            },
        )
        assert response.status_code == 201


@pytest.mark.asyncio(loop_scope="session")
async def test_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post(
            "/auth/register",
            json={
                "email": "test@te.st",
                "password": "test0123",
                "is_active": True,
                "is_superuser": False,
                "is_verified": False,
                "username": "tester",
                "telegram_username": "tg_tester",
            },
        )

        response = await ac.post(
            "/auth/jwt/login",
            data={
                "username": "test@te.st",
                "password": "test0123",
                "scope": "",
                "client_id": "",
                "client_secret": "",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_tg_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post(
            "/auth/register",
            json={
                "email": "test@te.st",
                "password": "test0123",
                "is_active": True,
                "is_superuser": False,
                "is_verified": False,
                "username": "tester",
                "telegram_username": "tg_tester",
            },
        )

        response = await ac.post(
            "/auth/tg/login?telegram_username=tg_tester",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
