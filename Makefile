.DEFAULT_GOAL := help

# =============================================================================
# Semantic Search - Makefile
# =============================================================================

PYTHON := $(if $(wildcard ./venv/bin/python),$(CURDIR)/venv/bin/python,python3)

help:
	@echo "=============================================="
	@echo "  Semantic Search - Available commands"
	@echo "=============================================="
	@echo ""
	@echo "DOCKER (backend + frontend + PostgreSQL + pgVector):"
	@echo "  make up                 - Start all containers"
	@echo "  make down               - Stop and remove containers"
	@echo "  make build              - Build backend image"
	@echo "  make build-test         - Build test stage"
	@echo "  make test-docker        - Run tests inside container"
	@echo "  make logs               - Follow container logs"
	@echo ""
	@echo "SETUP (local):"
	@echo "  make setup              - Full setup (venv + deps + db)"
	@echo "  make setup-venv        - Create virtual environment"
	@echo "  make install           - Install production deps"
	@echo "  make install-dev       - Install dev/test deps"
	@echo ""
	@echo "DATABASE:"
	@echo "  make db-up             - Start PostgreSQL + pgVector only"
	@echo "  make db-down           - Stop PostgreSQL"
	@echo "  make db-reset          - Remove volume and recreate"
	@echo ""
	@echo "EXECUTION (local, with venv activated):"
	@echo "  make ingest            - Ingest PDF into vector store"
	@echo "  make chat              - Start chat CLI (direct)"
	@echo "  make chat-api          - Start chat CLI (via API)"
	@echo "  make serve             - Start FastAPI backend (dev)"
	@echo "  make web               - Start Streamlit frontend"
	@echo "  make run               - Ingest then serve"
	@echo ""
	@echo "TEST:"
	@echo "  make test              - Run unit tests locally"
	@echo "  make test-docker       - Run unit tests in container"
	@echo ""
	@echo "UTILS:"
	@echo "  make clean             - Remove __pycache__ and .pyc"
	@echo ""

# -----------------------------------------------------------------------------
# SETUP
# -----------------------------------------------------------------------------

setup: setup-venv install db-up
	@echo "Setup completo. Execute: make run"

setup-venv:
	@test -d venv || python3 -m venv venv
	@echo "Virtual environment criado em ./venv"
	@echo "Ative com: source venv/bin/activate"

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r backend/requirements.txt

install-dev:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r backend/requirements-dev.txt

# -----------------------------------------------------------------------------
# DOCKER
# -----------------------------------------------------------------------------

up: build
	docker compose up -d
	@echo "Aguardando servicos..."
	@sleep 5
	@echo "Backend: http://localhost:8000  |  Frontend: http://localhost:3000  |  PostgreSQL: localhost:5432"

down:
	docker compose down

build:
	docker compose build

build-test:
	docker build -f backend/Dockerfile --target test .

logs:
	docker compose logs -f

# -----------------------------------------------------------------------------
# DATABASE
# -----------------------------------------------------------------------------

db-up:
	docker compose up -d postgres pgvector-setup
	@echo "Aguardando PostgreSQL ficar healthy..."
	@sleep 5
	@echo "PostgreSQL + pgVector rodando na porta 5432"

db-down:
	docker compose down

db-reset:
	docker compose down -v
	docker compose up -d postgres pgvector-setup
	@sleep 5
	@echo "Database resetado"

# -----------------------------------------------------------------------------
# EXECUCAO
# -----------------------------------------------------------------------------

ingest:
	cd backend && PYTHONPATH=. $(PYTHON) -m app.controllers.ingestion_controller

chat:
	PYTHONPATH=backend $(PYTHON) -m cli.cli

chat-api:
	$(PYTHON) -m cli.api_cli

serve:
	cd backend && PYTHONPATH=. $(PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app

web:
	cd frontend && npm run dev

run: ingest serve

# -----------------------------------------------------------------------------
# TEST
# -----------------------------------------------------------------------------

test:
	PYTHONPATH=backend $(PYTHON) -m pytest backend/tests/ -v

test-docker:
	docker compose --profile test run --rm backend-test

# -----------------------------------------------------------------------------
# UTILS
# -----------------------------------------------------------------------------

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
