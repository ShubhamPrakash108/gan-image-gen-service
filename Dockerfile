# syntax=docker/dockerfile:1
FROM python:3.10-slim-bullseye
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 ffmpeg \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt \
 && find /usr/local/lib/python3.10 -name "*.pyc" -delete \
 && find /usr/local/lib/python3.10 -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

COPY src ./src
COPY config ./config
COPY static ./static
COPY model ./model

EXPOSE 8080
CMD ["sh", "-c", "python -m src.worker.image_worker & uvicorn src.fastapi.api_main:app --host 0.0.0.0 --port ${PORT:-8080}"]