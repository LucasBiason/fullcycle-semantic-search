"""Tests for app.routes.health_route."""

from datetime import datetime
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routes.health_route import router


def _build_app():
    app = FastAPI()
    app.include_router(router)
    return app


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------


def test_health_returns_200():
    """Verifica que o endpoint /health retorna status HTTP 200 em condicoes normais."""
    with (
        patch("app.routes.health_route.embedding_service") as mock_svc,
        patch("app.routes.health_route.settings") as mock_settings,
    ):
        mock_svc.get_provider_name.return_value = "gemini"
        mock_settings.pg_vector_collection_name = "test_collection"

        client = TestClient(_build_app())
        response = client.get("/health")

    assert response.status_code == 200


def test_health_response_contains_healthy_status():
    """Verifica que o campo 'status' da resposta do endpoint /health tem o valor 'healthy'."""
    with (
        patch("app.routes.health_route.embedding_service") as mock_svc,
        patch("app.routes.health_route.settings") as mock_settings,
    ):
        mock_svc.get_provider_name.return_value = "gemini"
        mock_settings.pg_vector_collection_name = "test_collection"

        client = TestClient(_build_app())
        response = client.get("/health")

    assert response.json()["status"] == "healthy"


def test_health_response_contains_provider_from_service():
    """Verifica que o campo 'provider' da resposta reflete o valor retornado por embedding_service."""
    with (
        patch("app.routes.health_route.embedding_service") as mock_svc,
        patch("app.routes.health_route.settings") as mock_settings,
    ):
        mock_svc.get_provider_name.return_value = "openai"
        mock_settings.pg_vector_collection_name = "any_collection"

        client = TestClient(_build_app())
        response = client.get("/health")

    assert response.json()["provider"] == "openai"


def test_health_response_contains_collection_from_settings():
    """Verifica que o campo 'collection' da resposta reflete o valor de settings.pg_vector_collection_name."""
    with (
        patch("app.routes.health_route.embedding_service") as mock_svc,
        patch("app.routes.health_route.settings") as mock_settings,
    ):
        mock_svc.get_provider_name.return_value = "gemini"
        mock_settings.pg_vector_collection_name = "my_embeddings"

        client = TestClient(_build_app())
        response = client.get("/health")

    assert response.json()["collection"] == "my_embeddings"


def test_health_response_contains_iso_timestamp():
    """Verifica que o campo 'timestamp' da resposta e um timestamp ISO com informacao de fuso horario."""
    with (
        patch("app.routes.health_route.embedding_service") as mock_svc,
        patch("app.routes.health_route.settings") as mock_settings,
    ):
        mock_svc.get_provider_name.return_value = "gemini"
        mock_settings.pg_vector_collection_name = "test_collection"

        client = TestClient(_build_app())
        response = client.get("/health")

    timestamp = response.json()["timestamp"]
    assert timestamp is not None
    parsed = datetime.fromisoformat(timestamp)
    assert parsed.tzinfo is not None


def test_health_calls_get_provider_name():
    """Verifica que o endpoint /health chama get_provider_name uma unica vez no embedding_service."""
    with (
        patch("app.routes.health_route.embedding_service") as mock_svc,
        patch("app.routes.health_route.settings") as mock_settings,
    ):
        mock_svc.get_provider_name.return_value = "gemini"
        mock_settings.pg_vector_collection_name = "test_collection"

        client = TestClient(_build_app())
        client.get("/health")

    mock_svc.get_provider_name.assert_called_once()


def test_health_response_keys():
    """Verifica que a resposta do endpoint /health contem exatamente as chaves esperadas."""
    with (
        patch("app.routes.health_route.embedding_service") as mock_svc,
        patch("app.routes.health_route.settings") as mock_settings,
    ):
        mock_svc.get_provider_name.return_value = "gemini"
        mock_settings.pg_vector_collection_name = "test_collection"

        client = TestClient(_build_app())
        response = client.get("/health")

    body = response.json()
    assert set(body.keys()) == {"status", "provider", "collection", "timestamp"}


def test_health_uses_different_providers():
    """Verifica que o endpoint /health reflete corretamente diferentes provedores de embedding."""
    for provider in ["gemini", "openai", "custom-provider"]:
        with (
            patch("app.routes.health_route.embedding_service") as mock_svc,
            patch("app.routes.health_route.settings") as mock_settings,
        ):
            mock_svc.get_provider_name.return_value = provider
            mock_settings.pg_vector_collection_name = "col"

            client = TestClient(_build_app())
            response = client.get("/health")

        assert response.json()["provider"] == provider
