import re

from fastapi import APIRouter, Depends, Query
from fastapi_users import FastAPIUsers
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.service import auth_backend
from src.auth.manager import get_user_manager
from src.constants import EMPTY_LIST, INVALID_TG, UNKNOWN
from src.database import get_async_session
from src.exceptions import ErrorHTTPException
from src.users.models import User
from src.users.schemas import UserRead, UserUpdate

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)

router = APIRouter()

router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
)


@router.get("/users", response_model=list[UserRead])
async def get_users(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        query = select(User)
        result = await session.execute(query)
        return result.mappings().all()[offset:][:limit]
    except Exception as e:
        return ErrorHTTPException(status_code=400, error_code=EMPTY_LIST, detail=str(e))


@router.post("/link_tg")
async def link_tg(
    tg_username: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    tg_username_pattern = r"^[a-zA-Z0-9_]{5,32}$"
    if not re.match(tg_username_pattern, tg_username):
        return ErrorHTTPException(
            status_code=400, error_code=INVALID_TG, detail="Invalid telegram username"
        )

    try:
        stmt = (
            update(User).where(User.id == user.id).values(telegram_username=tg_username)
        )
        await session.execute(stmt)
        await session.commit()
        return {"status_code": "success", "detail": "Telegram username updated"}
    except Exception as e:
        return ErrorHTTPException(status_code=400, error_code=UNKNOWN, detail=str(e))
