from pydantic import BaseModel


class Bench(BaseModel):
    name: str
    description: str | None
    latitude: float
    longitude: float
    count: int


class BenchRead(Bench):
    id: int
    creator_id: int | None


class BenchCreate(Bench):
    pass
