"""FastAPI application setup with middleware stack and route registration."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.middleware.error_handler import CatchExceptionsMiddleware
from app.middleware.logging_middleware import LoggingMiddleware
from app.routes.health_route import router as health_router
from app.routes.ingestion_route import router as ingestion_router
from app.routes.search_route import router as search_router
from app.services.embedding_service import embedding_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("semantic_search")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    provider = embedding_service.get_provider_name()
    logger.info("[startup] Semantic Search API starting...")
    logger.info("[startup] Provider: %s", provider)
    logger.info("[startup] Collection: %s", settings.pg_vector_collection_name)
    yield
    logger.info("[shutdown] Semantic Search API shutting down...")


app = FastAPI(
    title="Semantic Search API",
    description="RAG-powered semantic search over PDF documents",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(CatchExceptionsMiddleware)

app.include_router(health_router)
app.include_router(ingestion_router)
app.include_router(search_router)
