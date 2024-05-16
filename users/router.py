import re

from fastapi import APIRouter, Depends
from fastapi_users import FastAPIUsers
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_backend
from auth.manager import get_user_manager
from database import get_async_session
from models.models import User

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)

router = APIRouter(
        tags=["users"]
)

@router.get("/users")
async def get_users(limit: int, offset: int, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(User)
        result = await session.execute(query)
        return {"status": "success",
                "data": result.mappings().all()[offset:][:limit],
                "details": None}
    except Exception:
        return {"status": "error"}


@router.post("/link_tg")
async def link_tg(tg_username: str, session: AsyncSession = Depends(get_async_session),
                  user: User = Depends(current_active_user)):
    tg_username_pattern = r'^[a-zA-Z0-9_]{5,32}$'
    if not re.match(tg_username_pattern, tg_username):
        return {"status": "error", "message": "Некорректный Telegram username"}

    try:
        stmt = update(User).where(User.id == user.id).values(telegram_username=tg_username)
        await session.execute(stmt)
        await session.commit()
        return {"status": "success"}
    except SQLAlchemyError as e:
        return {"status": "error", "message": str(e)}
