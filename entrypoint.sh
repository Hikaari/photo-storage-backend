#!/bin/bash
set -e

# echo ">>> Running migrations..."
# если у тебя есть alembic — раскомментируй:
# alembic upgrade head || { echo "Alembic failed"; exit 1; }

echo ">>> Starting application..."
exec python -m uvicorn src.main:app --host 0.0.0.0 --port 8000

