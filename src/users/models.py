from typing import List, Optional
import datetime
from sqlalchemy import String, TIMESTAMP, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    username: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    telegram_username: Mapped[Optional[str]] = mapped_column(
        String(64), unique=True, nullable=True
    )
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)
    registered_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, default=datetime.datetime.utcnow
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    benches: Mapped[List["Bench"]] = relationship("Bench", back_populates="creator")

    def __repr__(self) -> str:
        return (
            f"User(id={self.id!r}, email={self.email!r}, "
            f"username={self.username!r}, telegram_username={self.telegram_username!r}, "
            f"registered_at={self.registered_at!r}, is_active={self.is_active!r}, "
            f"is_superuser={self.is_superuser!r}, is_verified={self.is_verified!r})"
        )
