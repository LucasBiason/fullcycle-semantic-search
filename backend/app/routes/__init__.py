from app.routes.health_route import router as health_router
from app.routes.ingestion_route import router as ingestion_router
from app.routes.search_route import router as search_router

__all__ = ["health_router", "ingestion_router", "search_router"]
