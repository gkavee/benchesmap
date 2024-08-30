import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
async def test_register(ac: AsyncClient):
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
async def test_login(ac: AsyncClient):
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
async def test_tg_login(ac: AsyncClient):
    response = await ac.post(
        "/auth/tg/login?telegram_username=tg_tester",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
