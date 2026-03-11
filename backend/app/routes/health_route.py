"""Health check route."""

from datetime import datetime, timezone

from fastapi import APIRouter

from app.config import settings
from app.services.embedding_service import embedding_service

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    """Health check endpoint with provider and collection info."""
    return {
        "status": "healthy",
        "provider": embedding_service.get_provider_name(),
        "collection": settings.pg_vector_collection_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
