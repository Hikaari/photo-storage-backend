FROM python:3.12-slim
WORKDIR /app

# (опционально для psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

COPY src/ ./src
# если используешь файл, а не папку config:
COPY config.yaml ./config.yaml

EXPOSE 8000
# ключевой момент — запуск модулем
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

