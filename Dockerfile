FROM python:3.11-slim AS builder

WORKDIR /app

RUN pip install uv

COPY requirements.txt .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install --no-cache -r requirements.txt

FROM python:3.11

RUN apt-get update && apt-get install -y wait-for-it

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY . .

#CMD ["wait-for-it", "db:5432", "--", "alembic", "upgrade", "head", "&&", "gunicorn", "src.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:5002"]
