from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.benches.router import router as benches_router
from src.config import REDIS_HOST, REDIS_PORT
from src.users.router import router as users_router
from src.auth.router import router as auth_router
from src.error_handlers import setup_error_handlers

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis


tags_metadata = [
    {"name": "Benches", "description": "Operations with benches"},
    {"name": "Users", "description": "Operations with users"},
    {"name": "Authorization", "description": "Authorization logic"},
]

app = FastAPI(title="Bench app", docs_url="/api", openapi_tags=tags_metadata)

setup_error_handlers(app)

app.include_router(benches_router, tags=["Benches"])
app.include_router(users_router, tags=["Users"])
app.include_router(auth_router, tags=["Authorization"])

origins = [
    "https://localhost:8000",
    "https://localhost:5173",
    "https://localhost:5001",
    "https://localhost:5002",
    "http://localhost:5001",
    "http://localhost:5002",
    "https://f4c676c6e47e.vps.myjino.ru:49379",
    "https://f4c676c6e47e.vps.myjino.ru",
    "https://api.fitji.ru",
    "https://fitji.ru",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Cookie",
        "Set-Cookie",
        "Access-Control-Allow-Credential",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Methods",
        "Authorization",
    ],
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    redis = aioredis.from_url(
        f"redis://{REDIS_HOST}:{REDIS_PORT}", encoding="utf8", decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    try:
        yield
    finally:
        pass
