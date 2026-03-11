"""Tests for app.schemas.ingestion - IngestResponse."""

import pytest
from pydantic import ValidationError

from app.schemas.ingestion import IngestResponse


# ---------------------------------------------------------------------------
# IngestResponse
# ---------------------------------------------------------------------------


def test_ingest_response_valid_construction():
    """Verifica que IngestResponse e construida corretamente com todos os campos validos."""
    response = IngestResponse(
        status="success",
        message="Ingestion completed",
        pdf_path="assets/document.pdf",
        chunks_stored=42,
    )
    assert response.status == "success"
    assert response.message == "Ingestion completed"
    assert response.pdf_path == "assets/document.pdf"
    assert response.chunks_stored == 42


def test_ingest_response_all_fields_required():
    """Verifica que instanciar IngestResponse sem nenhum campo levanta ValidationError."""
    with pytest.raises(ValidationError):
        IngestResponse()


def test_ingest_response_missing_status_raises():
    """Verifica que omitir o campo status levanta ValidationError."""
    with pytest.raises(ValidationError):
        IngestResponse(
            message="Ingestion completed",
            pdf_path="assets/document.pdf",
            chunks_stored=5,
        )


def test_ingest_response_missing_message_raises():
    """Verifica que omitir o campo message levanta ValidationError."""
    with pytest.raises(ValidationError):
        IngestResponse(
            status="success",
            pdf_path="assets/document.pdf",
            chunks_stored=5,
        )


def test_ingest_response_missing_pdf_path_raises():
    """Verifica que omitir o campo pdf_path levanta ValidationError."""
    with pytest.raises(ValidationError):
        IngestResponse(
            status="success",
            message="Done",
            chunks_stored=5,
        )


def test_ingest_response_missing_chunks_stored_raises():
    """Verifica que omitir o campo chunks_stored levanta ValidationError."""
    with pytest.raises(ValidationError):
        IngestResponse(
            status="success",
            message="Done",
            pdf_path="assets/document.pdf",
        )


def test_ingest_response_chunks_stored_zero_is_valid():
    """Verifica que chunks_stored=0 e um valor valido (nenhum chunk gerado)."""
    response = IngestResponse(
        status="warning",
        message="No chunks generated",
        pdf_path="assets/empty.pdf",
        chunks_stored=0,
    )
    assert response.chunks_stored == 0


def test_ingest_response_serialization_to_dict():
    """Verifica que IngestResponse serializa corretamente para dicionario via model_dump."""
    response = IngestResponse(
        status="success",
        message="Done",
        pdf_path="assets/document.pdf",
        chunks_stored=10,
    )
    data = response.model_dump()
    assert data == {
        "status": "success",
        "message": "Done",
        "pdf_path": "assets/document.pdf",
        "chunks_stored": 10,
    }


def test_ingest_response_serialization_to_json():
    """Verifica que IngestResponse serializa corretamente para JSON via model_dump_json."""
    response = IngestResponse(
        status="success",
        message="Done",
        pdf_path="assets/document.pdf",
        chunks_stored=7,
    )
    json_str = response.model_dump_json()
    assert '"status":"success"' in json_str
    assert '"chunks_stored":7' in json_str


def test_ingest_response_chunks_stored_must_be_int():
    """Verifica que chunks_stored com valor nao-inteiro levanta ValidationError."""
    with pytest.raises(ValidationError):
        IngestResponse(
            status="success",
            message="Done",
            pdf_path="assets/document.pdf",
            chunks_stored="not-an-int",
        )
