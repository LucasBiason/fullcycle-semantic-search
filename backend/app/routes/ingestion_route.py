"""Ingestion route. Thin layer that delegates to controller."""

from fastapi import APIRouter

from app.config import settings
from app.controllers.ingestion_controller import IngestionController
from app.schemas.ingestion import IngestResponse

router = APIRouter(prefix="/api", tags=["ingestion"])


@router.post("/ingest", response_model=IngestResponse)
def ingest() -> IngestResponse:
    """Run PDF ingestion pipeline using the configured PDF path."""
    controller = IngestionController()
    count = controller.ingest_pdf()
    return IngestResponse(
        status="success",
        message="PDF ingested successfully",
        pdf_path=settings.pdf_path,
        chunks_stored=count,
    )
