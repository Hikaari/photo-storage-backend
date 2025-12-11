#!/bin/bash
set -e

echo ">>> Backend entrypoint"
echo ">>> APP_MODE=${APP_MODE:-default}"
echo ">>> RUN_MIGRATIONS_ON_START=${RUN_MIGRATIONS_ON_START:-true}"

run_migrations() {
  echo ">>> Running DB migrations..."

    alembic upgrade head
    echo ">>> Alembic migrations completed"

}

start_app() {
  echo ">>> Starting application with uvicorn..."
  exec python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
}

MODE="${APP_MODE:-default}"

case "$MODE" in
  migrate)
    # Только миграции, потом выходим
    run_migrations
    echo ">>> APP_MODE=migrate: exiting after migrations"
    ;;

  nomigrate)
# По умолчанию: миграции (если не отключены) + приложение
    if [ "${RUN_MIGRATIONS_ON_START:-true}" = "true" ]; then
      run_migrations
    else
      echo ">>> RUN_MIGRATIONS_ON_START=false: skipping migrations"
    fi
    start_app
    ;;


  default|serve|*)   

# Только приложение, без миграций
    echo ">>> APP_MODE=nomigrate: skipping migrations"
    start_app
    ;;

esac

