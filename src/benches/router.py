from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_users import FastAPIUsers
from sqlalchemy import select, insert, func, delete, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.service import auth_backend
from src.constants import EMPTY_LIST, UNKNOWN, NOT_FOUND, VALIDATION_ERROR
from src.database import get_async_session
from src.auth.manager import get_user_manager
from src.benches.schemas import BenchCreate, BenchRead
from src.benches.models import Bench
from src.users.models import User

from fastapi_cache.decorator import cache

from src.exceptions import ErrorHTTPException

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)

router = APIRouter()


@router.get("/benches", response_model=list[BenchRead])
@cache(expire=60)
async def get_benches(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        query = select(Bench)
        result = await session.execute(query)
        benches = result.scalars().all()
        return benches[offset:][:limit]
    except Exception as e:
        return ErrorHTTPException(status_code=400, error_code=EMPTY_LIST, detail=str(e))


@router.get("/bench/{bench_id}", response_model=BenchRead)
async def get_bench(bench_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(Bench).where(bench_id == Bench.id)
        result = await session.execute(query)
        bench = result.scalar_one_or_none()
        if bench is None:
            raise ErrorHTTPException(
                status_code=400, error_code=EMPTY_LIST, detail="Bench not found"
            )
        return bench
    except Exception as e:
        return ErrorHTTPException(status_code=400, error_code=UNKNOWN, detail=str(e))


@router.get("/nearest_bench/", response_model=BenchRead)
async def get_nearest_bench(
    latitude: float,
    longitude: float,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        result = await session.execute(
            select(Bench).order_by(
                func.pow(Bench.latitude - latitude, 2)
                + func.pow(Bench.longitude - longitude, 2)
            )
        )
        nearest_bench = result.scalars().first()
        return nearest_bench
    except Exception as e:
        return ErrorHTTPException(status_code=400, error_code=UNKNOWN, detail=str(e))


@router.post("/bench/create", response_model=BenchRead)
async def create_bench(
    operation: BenchCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    try:
        stmt = (
            insert(Bench)
            .values(**operation.model_dump(exclude={"creator_id"}), creator_id=user.id)
            .returning(Bench.id)
        )
        result = await session.execute(stmt)
        created_bench_id = result.scalar_one()

        stmt = select(Bench).where(Bench.id == created_bench_id)
        result = await session.execute(stmt)
        created_bench = result.scalar_one()

        await session.commit()

        return BenchRead(
            id=created_bench.id,
            name=created_bench.name,
            description=created_bench.description,
            count=created_bench.count,
            latitude=created_bench.latitude,
            longitude=created_bench.longitude,
            creator_id=created_bench.creator_id,
        )

    except SQLAlchemyError as e:
        return ErrorHTTPException(
            status_code=400, error_code=VALIDATION_ERROR, detail=str(e)
        )

    except Exception as e:
        return ErrorHTTPException(status_code=400, error_code=UNKNOWN, detail=str(e))


@router.delete("/bench/delete")
async def delete_bench(
    bench_name: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    try:
        stmt = delete(Bench).where(
            and_(Bench.name == bench_name, Bench.creator_id == user.id)
        )
        result = await session.execute(stmt)
        if result.rowcount > 0:
            await session.commit()
            return {"status_code": "200", "detail": f"Bench {bench_name} deleted"}
        else:
            return ErrorHTTPException(
                status_code=400,
                error_code=NOT_FOUND,
                detail="Bench not found or you aren't creator!",
            )
    except Exception as e:
        return ErrorHTTPException(status_code=400, error_code=UNKNOWN, detail=str(e))
