"""Tests for app.routes.search_route."""

from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routes.search_route import router


def _build_app():
    app = FastAPI()
    app.include_router(router)
    return app


# ---------------------------------------------------------------------------
# POST /api/search
# ---------------------------------------------------------------------------


def test_search_returns_200_for_valid_request():
    """Verifica que o endpoint POST /api/search retorna status HTTP 200 para uma requisicao valida."""
    with patch("app.routes.search_route.SearchController") as mock_ctrl_cls:
        mock_ctrl = MagicMock()
        mock_ctrl.ask.return_value = "The answer."
        mock_ctrl_cls.return_value = mock_ctrl

        client = TestClient(_build_app())
        response = client.post(
            "/api/search", json={"question": "What is pgvector?"}
        )

    assert response.status_code == 200


def test_search_response_contains_answer():
    """Verifica que o campo 'answer' da resposta contem o texto retornado pelo SearchController."""
    with patch("app.routes.search_route.SearchController") as mock_ctrl_cls:
        mock_ctrl = MagicMock()
        mock_ctrl.ask.return_value = "pgvector is an extension."
        mock_ctrl_cls.return_value = mock_ctrl

        client = TestClient(_build_app())
        response = client.post(
            "/api/search", json={"question": "What is pgvector?"}
        )

    assert response.json()["answer"] == "pgvector is an extension."


def test_search_response_only_has_answer_key():
    """Verifica que a resposta de busca contem apenas a chave 'answer' no corpo JSON."""
    with patch("app.routes.search_route.SearchController") as mock_ctrl_cls:
        mock_ctrl = MagicMock()
        mock_ctrl.ask.return_value = "Answer."
        mock_ctrl_cls.return_value = mock_ctrl

        client = TestClient(_build_app())
        response = client.post(
            "/api/search", json={"question": "Schema keys question"}
        )

    assert set(response.json().keys()) == {"answer"}


def test_search_passes_question_to_controller():
    """Verifica que o texto da pergunta enviado na requisicao e repassado ao metodo ask do SearchController."""
    with patch("app.routes.search_route.SearchController") as mock_ctrl_cls:
        mock_ctrl = MagicMock()
        mock_ctrl.ask.return_value = "Answer."
        mock_ctrl_cls.return_value = mock_ctrl

        client = TestClient(_build_app())
        client.post("/api/search", json={"question": "My specific question"})

    mock_ctrl.ask.assert_called_once()
    call_args = mock_ctrl.ask.call_args
    assert call_args.args[0] == "My specific question"


def test_search_passes_default_k_to_controller():
    """Verifica que o valor padrao de k e passado ao SearchController quando nao informado na requisicao."""
    with patch("app.routes.search_route.SearchController") as mock_ctrl_cls:
        mock_ctrl = MagicMock()
        mock_ctrl.ask.return_value = "Answer."
        mock_ctrl_cls.return_value = mock_ctrl

        client = TestClient(_build_app())
        client.post("/api/search", json={"question": "Test default k value"})

    call_args = mock_ctrl.ask.call_args
    assert call_args.kwargs.get("k") == 20


def test_search_passes_custom_k_to_controller():
    """Verifica que o valor customizado de k informado na requisicao e repassado ao SearchController."""
    with patch("app.routes.search_route.SearchController") as mock_ctrl_cls:
        mock_ctrl = MagicMock()
        mock_ctrl.ask.return_value = "Answer."
        mock_ctrl_cls.return_value = mock_ctrl

        client = TestClient(_build_app())
        client.post("/api/search", json={"question": "Custom k question?", "k": 5})

    call_args = mock_ctrl.ask.call_args
    assert call_args.kwargs.get("k") == 5


def test_search_instantiates_controller_per_request():
    """Verifica que o SearchController e instanciado uma vez por requisicao POST /api/search."""
    with patch("app.routes.search_route.SearchController") as mock_ctrl_cls:
        mock_ctrl = MagicMock()
        mock_ctrl.ask.return_value = "Answer."
        mock_ctrl_cls.return_value = mock_ctrl

        client = TestClient(_build_app())
        client.post("/api/search", json={"question": "First question here"})
        client.post("/api/search", json={"question": "Second question here"})

    assert mock_ctrl_cls.call_count == 2


def test_search_returns_422_when_question_too_short():
    """Verifica que o endpoint retorna 422 quando a pergunta enviada e curta demais para ser valida."""
    client = TestClient(_build_app())
    response = client.post("/api/search", json={"question": "Hi"})
    assert response.status_code == 422


def test_search_returns_422_when_question_missing():
    """Verifica que o endpoint retorna 422 quando o campo obrigatorio 'question' nao e enviado."""
    client = TestClient(_build_app())
    response = client.post("/api/search", json={"k": 5})
    assert response.status_code == 422


def test_search_returns_422_when_k_out_of_range():
    """Verifica que o endpoint retorna 422 quando o valor de k esta fora do intervalo permitido."""
    client = TestClient(_build_app())
    response = client.post(
        "/api/search", json={"question": "Valid question text", "k": 100}
    )
    assert response.status_code == 422
