from typing import Optional

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base import Base
from src.users.models import User


class Bench(Base):
    __tablename__ = "benches"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(36), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    count: Mapped[Optional[int]] = mapped_column(Integer, default=1, nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=False)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=False)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    creator: Mapped[User] = relationship("User", back_populates="benches")

    def __repr__(self) -> str:
        return (
            f"Bench(id={self.id!r}, name={self.name!r}, description={self.description!r}, "
            f"count={self.count!r}, latitude={self.latitude!r}, longitude={self.longitude!r}, "
            f"creator_id={self.creator_id!r})"
        )
