"""Pydantic schemas for ingestion domain."""

from pydantic import BaseModel


class IngestResponse(BaseModel):
    status: str
    message: str
    pdf_path: str
    chunks_stored: int
