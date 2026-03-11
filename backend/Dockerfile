# Multi-stage Dockerfile for backend (FastAPI).
# Build from repo root: docker build -f backend/Dockerfile .

# -----------------------------------------------------------------------------
# Stage 1: Production dependencies only
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS deps

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Test runner (install dev deps and run tests; optional in CI)
# -----------------------------------------------------------------------------
FROM deps AS test

COPY backend/requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY backend/ ./backend/
COPY backend/tests/ ./backend/tests/

WORKDIR /app
ENV PYTHONPATH=/app/backend
RUN pytest backend/tests/ -v --cov=backend/app --cov-report=term-missing --cov-fail-under=0
CMD ["pytest", "backend/tests/", "-v"]

# -----------------------------------------------------------------------------
# Stage 3: Production runner (FastAPI backend)
# -----------------------------------------------------------------------------
FROM deps AS runner

COPY backend/app/ ./backend/app/
COPY backend/entrypoint.sh /entrypoint.sh
COPY assets/ ./assets/
RUN chmod +x /entrypoint.sh

ENV PYTHONPATH=/app/backend
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["prod"]
