import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi_users import FastAPIUsers
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_backend, get_jwt_strategy
from auth.manager import get_user_manager
from auth.schemas import UserRead, UserCreate, UserUpdate
from database import get_async_session
from models.models import User


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

'''
Telegram auth logic
'''
tg_login_router = APIRouter(prefix="/auth", tags=["auth"])


@tg_login_router.post("/tg/login")
async def tg_login(telegram_username: str, session: AsyncSession = Depends(get_async_session)):
    async with session.begin():
        stmt = select(User).where(User.telegram_username == telegram_username)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            strategy = get_jwt_strategy()
            response = await auth_backend.login(strategy, user)
            return response
        else:
            raise HTTPException(status_code=404, detail="User not found")

