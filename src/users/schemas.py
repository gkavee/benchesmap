from typing import Optional

from fastapi_users import schemas
from pydantic import EmailStr


class UserRead(schemas.BaseUser[int]):
    id: int
    email: EmailStr
    username: str
    telegram_username: Optional[str] = None
    is_active: bool = False
    is_superuser: bool = False
    is_verified: bool = False


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    password: str
    username: str
    telegram_username: Optional[str] = None
    is_active: bool = False
    is_superuser: bool = False
    is_verified: bool = False


class UserUpdate(schemas.BaseUserUpdate):
    email: EmailStr
    password: str
    username: str
    telegram_username: Optional[str] = None
    is_active: bool = False
    is_superuser: bool = False
    is_verified: bool = False
