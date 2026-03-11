"""Tests for app.middleware.logging_middleware."""

import logging
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.logging_middleware import LoggingMiddleware, SENSITIVE_HEADERS


def _build_app(custom_logger=None):
    """Build a minimal FastAPI app with LoggingMiddleware attached."""
    app = FastAPI()
    app.add_middleware(LoggingMiddleware, custom_logger=custom_logger)

    @app.get("/ok")
    def ok():
        return {"status": "ok"}

    @app.get("/boom")
    def boom():
        raise RuntimeError("intentional error")

    return app


# ---------------------------------------------------------------------------
# SENSITIVE_HEADERS / _safe_headers
# ---------------------------------------------------------------------------


def test_known_sensitive_headers_are_masked():
    """Verifica que todos os headers sensiveis conhecidos sao substituidos por '***'."""
    for header in SENSITIVE_HEADERS:
        result = LoggingMiddleware._safe_headers({header: "secret-value"})
        assert result[header] == "***", f"Expected {header} to be masked"


def test_non_sensitive_header_is_preserved():
    """Verifica que headers nao sensiveis sao preservados com seu valor original."""
    result = LoggingMiddleware._safe_headers({"content-type": "application/json"})
    assert result["content-type"] == "application/json"


def test_mixed_headers():
    """Verifica que headers sensiveis sao mascarados e nao sensiveis sao preservados simultaneamente."""
    headers = {
        "authorization": "Bearer token123",
        "cookie": "session=abc",
        "x-api-key": "mykey",
        "accept": "application/json",
        "x-custom": "visible",
    }
    result = LoggingMiddleware._safe_headers(headers)
    assert result["authorization"] == "***"
    assert result["cookie"] == "***"
    assert result["x-api-key"] == "***"
    assert result["accept"] == "application/json"
    assert result["x-custom"] == "visible"


def test_empty_headers():
    """Verifica que um dicionario vazio de headers retorna um dicionario vazio."""
    result = LoggingMiddleware._safe_headers({})
    assert result == {}


def test_sensitive_header_matching_is_case_insensitive():
    """Verifica que o mascaramento de headers sensiveis e insensivel a maiusculas/minusculas."""
    headers = {"Authorization": "Bearer token"}
    result = LoggingMiddleware._safe_headers(headers)
    assert result["Authorization"] == "***"


# ---------------------------------------------------------------------------
# LoggingMiddleware.__init__
# ---------------------------------------------------------------------------


def test_logging_middleware_uses_default_logger_when_none_provided():
    """Verifica que o middleware usa o logger padrao 'semantic_search' quando nenhum logger e fornecido."""
    app = FastAPI()
    middleware = LoggingMiddleware(app)
    assert middleware.logger.name == "semantic_search"


def test_logging_middleware_uses_custom_logger_when_provided():
    """Verifica que o middleware usa o logger customizado quando um e fornecido."""
    custom_logger = logging.getLogger("custom")
    app = FastAPI()
    middleware = LoggingMiddleware(app, custom_logger=custom_logger)
    assert middleware.logger is custom_logger


# ---------------------------------------------------------------------------
# dispatch - requisicoes normais
# ---------------------------------------------------------------------------


def test_normal_request_returns_200():
    """Verifica que uma requisicao normal passa pelo middleware retornando status 200 e corpo correto."""
    client = TestClient(_build_app())
    response = client.get("/ok")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_normal_request_logs_incoming_and_outgoing():
    """Verifica que uma requisicao normal registra os blocos INCOMING REQUEST, OUTGOING RESPONSE e END RESPONSE."""
    mock_logger = MagicMock()
    client = TestClient(_build_app(custom_logger=mock_logger))
    client.get("/ok")

    logged_messages = [call.args[0] for call in mock_logger.info.call_args_list]
    assert any("INCOMING REQUEST" in msg for msg in logged_messages)
    assert any("OUTGOING RESPONSE" in msg for msg in logged_messages)
    assert any("END RESPONSE" in msg for msg in logged_messages)


def test_normal_request_logs_method_and_status():
    """Verifica que uma requisicao normal registra o metodo HTTP e o status code da resposta."""
    mock_logger = MagicMock()
    client = TestClient(_build_app(custom_logger=mock_logger))
    client.get("/ok")

    info_calls = mock_logger.info.call_args_list
    logged_args = [(c.args[0], c.args[1:]) for c in info_calls]

    assert any("Method" in msg and "GET" in str(args) for msg, args in logged_args)
    assert any("Status Code" in msg and 200 in args for msg, args in logged_args)


def test_normal_request_logs_process_time():
    """Verifica que uma requisicao normal registra o tempo de processamento (Process Time)."""
    mock_logger = MagicMock()
    client = TestClient(_build_app(custom_logger=mock_logger))
    client.get("/ok")

    info_calls = [c.args[0] for c in mock_logger.info.call_args_list]
    assert any("Process Time" in msg for msg in info_calls)


def test_normal_request_logs_path():
    """Verifica que uma requisicao normal registra o caminho (Path) da URL."""
    mock_logger = MagicMock()
    client = TestClient(_build_app(custom_logger=mock_logger))
    client.get("/ok")

    info_calls = mock_logger.info.call_args_list
    logged_args = [(c.args[0], c.args[1:]) for c in info_calls]
    assert any("Path" in msg and "/ok" in str(args) for msg, args in logged_args)


# ---------------------------------------------------------------------------
# dispatch - requisicoes com erro
# ---------------------------------------------------------------------------


def test_error_request_logs_error_details():
    """Verifica que uma requisicao com erro registra os blocos REQUEST ERROR e END ERROR no logger."""
    mock_logger = MagicMock()
    client = TestClient(
        _build_app(custom_logger=mock_logger), raise_server_exceptions=False
    )
    client.get("/boom")

    error_calls = [c.args[0] for c in mock_logger.error.call_args_list]
    assert any("REQUEST ERROR" in msg for msg in error_calls)
    assert any("END ERROR" in msg for msg in error_calls)


def test_error_request_logs_error_type_and_message():
    """Verifica que uma requisicao com erro registra o tipo e a mensagem da excecao."""
    mock_logger = MagicMock()
    client = TestClient(
        _build_app(custom_logger=mock_logger), raise_server_exceptions=False
    )
    client.get("/boom")

    error_calls = [
        (c.args[0], c.args[1:]) for c in mock_logger.error.call_args_list
    ]
    assert any(
        "Error Type" in msg and "RuntimeError" in str(args)
        for msg, args in error_calls
    )
    assert any(
        "Error Message" in msg and "intentional error" in str(args)
        for msg, args in error_calls
    )


def test_error_request_logs_process_time_on_error():
    """Verifica que o tempo de processamento e registrado mesmo quando a requisicao resulta em erro."""
    mock_logger = MagicMock()
    client = TestClient(
        _build_app(custom_logger=mock_logger), raise_server_exceptions=False
    )
    client.get("/boom")

    error_calls = [c.args[0] for c in mock_logger.error.call_args_list]
    assert any("Process Time" in msg for msg in error_calls)


def test_error_request_reraises_exception():
    """Verifica que o middleware repropaga a excecao apos registra-la no logger."""
    client = TestClient(_build_app(), raise_server_exceptions=True)
    with pytest.raises(RuntimeError, match="intentional error"):
        client.get("/boom")


# ---------------------------------------------------------------------------
# mascaramento de headers nos logs
# ---------------------------------------------------------------------------


def test_sensitive_headers_are_masked_in_logs():
    """Verifica que headers sensiveis como Authorization nao aparecem em texto claro nos logs."""
    mock_logger = MagicMock()
    client = TestClient(_build_app(custom_logger=mock_logger))
    client.get(
        "/ok",
        headers={"Authorization": "Bearer supersecret", "X-Custom": "visible"},
    )

    all_info_args = str(mock_logger.info.call_args_list)
    assert "supersecret" not in all_info_args
    assert "***" in all_info_args


def test_non_sensitive_headers_are_visible_in_logs():
    """Verifica que headers nao sensiveis aparecem com seu valor real nos logs."""
    mock_logger = MagicMock()
    client = TestClient(_build_app(custom_logger=mock_logger))
    client.get("/ok", headers={"X-Trace-Id": "trace-abc-123"})

    all_info_args = str(mock_logger.info.call_args_list)
    assert "trace-abc-123" in all_info_args


def test_query_params_are_logged():
    """Verifica que os parametros de query string sao registrados nos logs da requisicao."""
    mock_logger = MagicMock()
    client = TestClient(_build_app(custom_logger=mock_logger))
    client.get("/ok?foo=bar&baz=qux")

    info_calls = mock_logger.info.call_args_list
    logged_args = [(c.args[0], c.args[1:]) for c in info_calls]
    assert any(
        "Query Params" in msg and "foo" in str(args) for msg, args in logged_args
    )


def test_client_info_is_logged():
    """Verifica que as informacoes do cliente (Client) sao registradas nos logs."""
    mock_logger = MagicMock()
    client = TestClient(_build_app(custom_logger=mock_logger))
    client.get("/ok")

    info_calls = [c.args[0] for c in mock_logger.info.call_args_list]
    assert any("Client" in msg for msg in info_calls)


def test_response_headers_are_logged():
    """Verifica que os headers da resposta sao registrados nos logs."""
    mock_logger = MagicMock()
    client = TestClient(_build_app(custom_logger=mock_logger))
    client.get("/ok")

    info_calls = mock_logger.info.call_args_list
    logged_messages = [c.args[0] for c in info_calls]
    assert any("Headers" in msg for msg in logged_messages)
