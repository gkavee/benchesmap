from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from src.auth.router import router as auth_router
from src.benches.router import router as benches_router
from src.config import REDIS_HOST, REDIS_PORT
from src.error_handlers import setup_error_handlers
from src.users.router import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    redis = aioredis.from_url(
        f"redis://{REDIS_HOST}:{REDIS_PORT}", encoding="utf8", decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    try:
        yield
    finally:
        await redis.close()


tags_metadata = [
    {"name": "Benches", "description": "Operations with benches"},
    {"name": "Users", "description": "Operations with users"},
    {"name": "Authorization", "description": "Authorization logic"},
]

app = FastAPI(
    title="Bench app", docs_url="/api", openapi_tags=tags_metadata, lifespan=lifespan
)

setup_error_handlers(app)

app.include_router(benches_router, tags=["Benches"])
app.include_router(users_router, tags=["Users"])
app.include_router(auth_router, tags=["Authorization"])
