"""Tests for app.routes.ingestion_route."""

from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routes.ingestion_route import router


def _build_app():
    app = FastAPI()
    app.include_router(router)
    return app


# ---------------------------------------------------------------------------
# POST /api/ingest
# ---------------------------------------------------------------------------


def test_ingest_returns_200():
    """Verifica que o endpoint POST /api/ingest retorna status HTTP 200 em condicoes normais."""
    with (
        patch("app.routes.ingestion_route.IngestionController") as mock_ctrl_cls,
        patch("app.routes.ingestion_route.settings") as mock_settings,
    ):
        mock_ctrl = MagicMock()
        mock_ctrl.ingest_pdf.return_value = 10
        mock_ctrl_cls.return_value = mock_ctrl
        mock_settings.pdf_path = "assets/document.pdf"

        client = TestClient(_build_app())
        response = client.post("/api/ingest")

    assert response.status_code == 200


def test_ingest_response_status_is_success():
    """Verifica que o campo 'status' da resposta de ingestao tem o valor 'success'."""
    with (
        patch("app.routes.ingestion_route.IngestionController") as mock_ctrl_cls,
        patch("app.routes.ingestion_route.settings") as mock_settings,
    ):
        mock_ctrl = MagicMock()
        mock_ctrl.ingest_pdf.return_value = 5
        mock_ctrl_cls.return_value = mock_ctrl
        mock_settings.pdf_path = "assets/document.pdf"

        client = TestClient(_build_app())
        response = client.post("/api/ingest")

    assert response.json()["status"] == "success"


def test_ingest_response_message():
    """Verifica que o campo 'message' da resposta de ingestao contem a mensagem de sucesso esperada."""
    with (
        patch("app.routes.ingestion_route.IngestionController") as mock_ctrl_cls,
        patch("app.routes.ingestion_route.settings") as mock_settings,
    ):
        mock_ctrl = MagicMock()
        mock_ctrl.ingest_pdf.return_value = 5
        mock_ctrl_cls.return_value = mock_ctrl
        mock_settings.pdf_path = "assets/document.pdf"

        client = TestClient(_build_app())
        response = client.post("/api/ingest")

    assert response.json()["message"] == "PDF ingested successfully"


def test_ingest_response_pdf_path_from_settings():
    """Verifica que o campo 'pdf_path' da resposta reflete o valor configurado em settings.pdf_path."""
    with (
        patch("app.routes.ingestion_route.IngestionController") as mock_ctrl_cls,
        patch("app.routes.ingestion_route.settings") as mock_settings,
    ):
        mock_ctrl = MagicMock()
        mock_ctrl.ingest_pdf.return_value = 3
        mock_ctrl_cls.return_value = mock_ctrl
        mock_settings.pdf_path = "custom/path/file.pdf"

        client = TestClient(_build_app())
        response = client.post("/api/ingest")

    assert response.json()["pdf_path"] == "custom/path/file.pdf"


def test_ingest_response_chunks_stored_from_controller():
    """Verifica que o campo 'chunks_stored' da resposta reflete o valor retornado por ingest_pdf."""
    with (
        patch("app.routes.ingestion_route.IngestionController") as mock_ctrl_cls,
        patch("app.routes.ingestion_route.settings") as mock_settings,
    ):
        mock_ctrl = MagicMock()
        mock_ctrl.ingest_pdf.return_value = 42
        mock_ctrl_cls.return_value = mock_ctrl
        mock_settings.pdf_path = "assets/document.pdf"

        client = TestClient(_build_app())
        response = client.post("/api/ingest")

    assert response.json()["chunks_stored"] == 42


def test_ingest_instantiates_controller_on_each_call():
    """Verifica que o IngestionController e instanciado uma vez por requisicao POST /api/ingest."""
    with (
        patch("app.routes.ingestion_route.IngestionController") as mock_ctrl_cls,
        patch("app.routes.ingestion_route.settings") as mock_settings,
    ):
        mock_ctrl = MagicMock()
        mock_ctrl.ingest_pdf.return_value = 1
        mock_ctrl_cls.return_value = mock_ctrl
        mock_settings.pdf_path = "assets/document.pdf"

        client = TestClient(_build_app())
        client.post("/api/ingest")
        client.post("/api/ingest")

    assert mock_ctrl_cls.call_count == 2


def test_ingest_calls_ingest_pdf():
    """Verifica que o metodo ingest_pdf do IngestionController e chamado exatamente uma vez por requisicao."""
    with (
        patch("app.routes.ingestion_route.IngestionController") as mock_ctrl_cls,
        patch("app.routes.ingestion_route.settings") as mock_settings,
    ):
        mock_ctrl = MagicMock()
        mock_ctrl.ingest_pdf.return_value = 7
        mock_ctrl_cls.return_value = mock_ctrl
        mock_settings.pdf_path = "assets/document.pdf"

        client = TestClient(_build_app())
        client.post("/api/ingest")

    mock_ctrl.ingest_pdf.assert_called_once()


def test_ingest_response_schema_keys():
    """Verifica que a resposta de ingestao contem exatamente as chaves de schema esperadas."""
    with (
        patch("app.routes.ingestion_route.IngestionController") as mock_ctrl_cls,
        patch("app.routes.ingestion_route.settings") as mock_settings,
    ):
        mock_ctrl = MagicMock()
        mock_ctrl.ingest_pdf.return_value = 0
        mock_ctrl_cls.return_value = mock_ctrl
        mock_settings.pdf_path = "assets/document.pdf"

        client = TestClient(_build_app())
        response = client.post("/api/ingest")

    body = response.json()
    assert set(body.keys()) == {"status", "message", "pdf_path", "chunks_stored"}


def test_ingest_with_zero_chunks():
    """Verifica que o endpoint retorna 200 e chunks_stored igual a zero quando nenhum chunk e processado."""
    with (
        patch("app.routes.ingestion_route.IngestionController") as mock_ctrl_cls,
        patch("app.routes.ingestion_route.settings") as mock_settings,
    ):
        mock_ctrl = MagicMock()
        mock_ctrl.ingest_pdf.return_value = 0
        mock_ctrl_cls.return_value = mock_ctrl
        mock_settings.pdf_path = "assets/document.pdf"

        client = TestClient(_build_app())
        response = client.post("/api/ingest")

    assert response.status_code == 200
    assert response.json()["chunks_stored"] == 0
