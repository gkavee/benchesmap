import uuid

from fastapi import APIRouter, Depends
from fastapi_users import FastAPIUsers
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.manager import get_user_manager
from src.auth.service import auth_backend, get_jwt_strategy
from src.constants import NOT_FOUND
from src.database import get_async_session
from src.exceptions import ErrorHTTPException
from src.users.models import User
from src.users.schemas import UserCreate, UserRead

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

router = APIRouter()

router.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt")

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
)

router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
)

router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
)

"""
Telegram auth logic
"""
tg_login_router = APIRouter(prefix="/auth")


@tg_login_router.post("/tg/login")
async def tg_login(
    telegram_username: str, session: AsyncSession = Depends(get_async_session)
):
    async with session.begin():
        stmt = select(User).where(User.telegram_username == telegram_username)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            strategy = get_jwt_strategy()
            response = await auth_backend.login(strategy, user)
            return response
        else:
            raise ErrorHTTPException(
                status_code=400, error_code=NOT_FOUND, detail="User not found"
            )


router.include_router(tg_login_router)
