#!/bin/sh

set -e

echo "Entrypoint: Database (db_calendar) is reported as healthy. Running migrations for calendar-service..."

alembic upgrade head

echo "Entrypoint: Migrations finished. Starting application (Uvicorn)..."

exec "$@"