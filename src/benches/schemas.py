from typing import Optional

from pydantic import BaseModel, HttpUrl


class Bench(BaseModel):
    name: str
    description: str | None
    latitude: float
    longitude: float
    count: int


class BenchRead(Bench):
    id: int
    creator_id: int | None
    photo_url: Optional[HttpUrl] = None


class BenchCreate(Bench):
    pass
