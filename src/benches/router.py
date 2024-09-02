import asyncio
from datetime import datetime

from fastapi import (APIRouter, BackgroundTasks, Depends, File, Query,
                     UploadFile)
from fastapi_cache.decorator import cache
from fastapi_users import FastAPIUsers
from google.api_core.retry import Retry
from google.auth.exceptions import TransportError
from google.cloud.exceptions import GoogleCloudError
from firebase_admin import storage
from sqlalchemy import and_, delete, func, insert, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.manager import get_user_manager
from src.auth.service import auth_backend
from src.benches.models import Bench
from src.benches.schemas import BenchCreate, BenchRead
from src.config import FIREBASE_BUCKET
from src.constants import EMPTY_LIST, NOT_FOUND, UNKNOWN, VALIDATION_ERROR
from src.database import get_async_session
from src.exceptions import ErrorHTTPException
from src.users.models import User

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


@router.get("/benches/{bench_id}", response_model=BenchRead)
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


@router.post("/create_bench", response_model=BenchRead)
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
            photo_url=created_bench.photo_url,
        )

    except SQLAlchemyError as e:
        return ErrorHTTPException(
            status_code=400, error_code=VALIDATION_ERROR, detail=str(e)
        )

    except Exception as e:
        return ErrorHTTPException(status_code=400, error_code=UNKNOWN, detail=str(e))


@router.delete("/delete_bench")
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


@router.post("/upload_bench_photo/{bench_id}")
async def upload_bench_photo(
    bench_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    content = await file.read()
    filename = f'bench{bench_id}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png'

    async def upload_to_cdn():
        try:
            bucket = storage.bucket()
            blob = bucket.blob(f"benches/{bench_id}/{filename}")

            retry_strategy = Retry(
                total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504]
            )
            blob._retry = retry_strategy

            await asyncio.wait_for(
                asyncio.to_thread(
                    blob.upload_from_string, content, content_type=file.content_type
                ),
                timeout=300,
            )

            blob.make_public()
            public_url = blob.public_url

            stmt = (
                update(Bench)
                .where(and_(Bench.id == bench_id, Bench.creator_id == user.id))
                .values(photo_url=public_url)
            )
            await session.execute(stmt)
            await session.commit()

        except (asyncio.TimeoutError, GoogleCloudError, TransportError) as e:
            print(f"An error occurred: {str(e)}")
            raise ErrorHTTPException(status_code=500, error_code=1100, detail="Failed to upload photo")

    background_tasks.add_task(upload_to_cdn)

    return {"status_code": "200", "filename": filename}
