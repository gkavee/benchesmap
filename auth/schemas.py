from typing import Optional

from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    id: int
    email: str
    username: str
    telegram_username: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserCreate(schemas.BaseUserCreate):
    email: str
    password: str
    username: str
    telegram_username: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserUpdate(schemas.BaseUserUpdate):
    email: str
    password: str
    username: str
    telegram_username: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
