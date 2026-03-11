#!/usr/bin/env bash

set -euo pipefail

cli_help() {
  local cli_name=${0##*/}
  echo "
$cli_name
Semantic Search - Entrypoint CLI
Usage: $cli_name [command]

Commands:
  dev       Start FastAPI with reload (development)
  prod      Start FastAPI (production)
  test      Run unit tests with coverage
  ingest    Run PDF ingestion into vector store
  health    Check dependencies and optional DB connectivity
  *         Display this help message

Environment Variables:
  API_PORT       API port (default: 8000)
  PDF_PATH       Path to PDF for ingest (default: assets/document.pdf)
"
  exit 1
}

wait_for_db() {
  if [ -z "${DATABASE_URL:-}" ]; then
    echo "WARNING: DATABASE_URL not set, skipping database check"
    return 0
  fi
  echo "Waiting for database..."
  DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
  DB_PORT=$(echo "$DATABASE_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p' || echo "5432")
  if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
    until nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; do
      echo "Database unavailable - sleeping"
      sleep 2
    done
    echo "Database is ready"
  fi
}

case "${1:-help}" in
  dev)
    echo "Starting FastAPI (development)..."
    wait_for_db
    cd /app
    exec python -m uvicorn app.main:app --host 0.0.0.0 --port "${API_PORT:-8000}" --reload --reload-dir backend/app
    ;;
  prod|runserver)
    echo "Starting FastAPI (production)..."
    wait_for_db
    cd /app
    exec python -m uvicorn app.main:app --host 0.0.0.0 --port "${API_PORT:-8000}" --workers 2
    ;;
  test)
    echo "Running tests with coverage..."
    cd /app
    exec pytest backend/tests/ -v --cov=backend/app --cov-report=term-missing --cov-report=html
    ;;
  ingest)
    echo "Running PDF ingestion..."
    wait_for_db
    cd /app/backend
    exec python -m app.controllers.ingestion_controller
    ;;
  health)
    echo "Health check: dependencies..."
    command -v python >/dev/null || { echo "ERROR: python not found"; exit 1; }
    python -c "import fastapi; import langchain_core" || { echo "ERROR: required modules missing"; exit 1; }
    wait_for_db || true
    echo "Health check OK"
    ;;
  *)
    cli_help
    ;;
esac
