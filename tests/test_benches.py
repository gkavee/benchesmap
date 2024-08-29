import pytest
from httpx import AsyncClient
from tests.conftest import app


@pytest.mark.asyncio(loop_scope="session")
async def test_get_benches():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/benches", params={"limit": 5, "offset": 0})
        assert response.status_code == 200
        assert isinstance(response.json(), list)
