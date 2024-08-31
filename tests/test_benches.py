import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.benches.models import Bench
from src.users.models import User


@pytest.fixture(scope="function")
async def authorized_client(ac: AsyncClient):
    await ac.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "username": "testuser",
        },
    )

    response = await ac.post(
        "/auth/jwt/login",
        data={
            "username": "test@example.com",
            "password": "testpassword",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    token = response.json()["token"]
    ac.cookies["token"] = token
    return ac


@pytest.fixture(scope="function")
async def test_benches(async_session: AsyncSession):
    await async_session.execute(Bench.__table__.delete())
    await async_session.execute(User.__table__.delete())
    await async_session.commit()

    user = User(
        email="creator@example.com",
        username="testus",
        telegram_username="tgtestus",
        hashed_password="hashed_password",
    )
    async_session.add(user)
    await async_session.flush()

    benches = [
        Bench(
            id=i,
            name=f"Bench {i}",
            description=f"Description {i}",
            count=i,
            latitude=i * 10,
            longitude=i * 10,
            creator_id=user.id,
        )
        for i in range(1, 6)
    ]
    async_session.add_all(benches)
    await async_session.commit()

    yield

    await async_session.execute(Bench.__table__.delete())
    await async_session.execute(User.__table__.delete())
    await async_session.commit()


@pytest.mark.asyncio
async def test_get_benches(authorized_client: AsyncClient, test_benches):
    response = await authorized_client.get("/benches")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert data[0]["name"] == "Bench 1"


@pytest.mark.asyncio
async def test_get_bench(authorized_client: AsyncClient, test_benches):
    response = await authorized_client.get("/benches/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Bench 1"


@pytest.mark.asyncio
async def test_get_nearest_bench(authorized_client: AsyncClient, test_benches):
    response = await authorized_client.get(
        "/nearest_bench/?latitude=15.015155&longitude=15.015155"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Bench 2"


@pytest.mark.asyncio
async def test_create_and_delete_bench(authorized_client: AsyncClient):
    bench_data = {
        "name": "New Bench",
        "description": "A new bench",
        "count": 1,
        "latitude": 50.0,
        "longitude": 50.0,
    }
    response = await authorized_client.post("/create_bench", json=bench_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Bench"

    response_delete = await authorized_client.delete(
        "/delete_bench", params={"bench_name": "New Bench"}
    )
    assert response_delete.status_code == 200
    data = response_delete.json()
    assert data["detail"] == "Bench New Bench deleted"
