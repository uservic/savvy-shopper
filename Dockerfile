FROM dockerhub.timeweb.cloud/library/python:3.11-slim

WORKDIR /app

# Отключаем буферизацию вывода Python и генерацию .pyc файлов
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY configs/ ./configs/
COPY src/ ./src/
COPY alembic.ini* ./
COPY alembic* ./alembic/
