"""Tests for app.middleware.error_handler."""

import json
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.exceptions import (
    IngestionError,
    ProviderNotConfiguredError,
    SearchError,
    VectorStoreError,
)
from app.middleware.error_handler import CatchExceptionsMiddleware, EXCEPTION_STATUS_MAP


def _build_app(raise_exc=None, custom_logger=None):
    """Build a minimal FastAPI app with CatchExceptionsMiddleware and a configurable endpoint."""
    app = FastAPI()
    app.add_middleware(CatchExceptionsMiddleware, custom_logger=custom_logger)

    @app.get("/trigger")
    def trigger():
        if raise_exc is not None:
            raise raise_exc
        return {"status": "ok"}

    return app


def _make_middleware():
    """Cria uma instancia de CatchExceptionsMiddleware para testes unitarios diretos."""
    app = FastAPI()
    return CatchExceptionsMiddleware(app)


# ---------------------------------------------------------------------------
# EXCEPTION_STATUS_MAP
# ---------------------------------------------------------------------------


def test_provider_not_configured_maps_to_503():
    """Verifica que ProviderNotConfiguredError esta mapeado para o status HTTP 503."""
    assert EXCEPTION_STATUS_MAP[ProviderNotConfiguredError] == 503


def test_ingestion_error_maps_to_500():
    """Verifica que IngestionError esta mapeado para o status HTTP 500."""
    assert EXCEPTION_STATUS_MAP[IngestionError] == 500


def test_search_error_maps_to_500():
    """Verifica que SearchError esta mapeado para o status HTTP 500."""
    assert EXCEPTION_STATUS_MAP[SearchError] == 500


def test_vector_store_error_maps_to_500():
    """Verifica que VectorStoreError esta mapeado para o status HTTP 500."""
    assert EXCEPTION_STATUS_MAP[VectorStoreError] == 500


def test_map_covers_exactly_four_exceptions():
    """Verifica que o mapa de excecoes contem exatamente quatro entradas."""
    assert len(EXCEPTION_STATUS_MAP) == 4


# ---------------------------------------------------------------------------
# CatchExceptionsMiddleware.__init__
# ---------------------------------------------------------------------------


def test_uses_default_logger_when_none_provided():
    """Verifica que o middleware usa o logger padrao 'semantic_search' quando nenhum logger e fornecido."""
    app = FastAPI()
    middleware = CatchExceptionsMiddleware(app)
    assert middleware.logger.name == "semantic_search"


def test_uses_custom_logger_when_provided():
    """Verifica que o middleware usa o logger customizado quando um e fornecido."""
    custom = MagicMock()
    app = FastAPI()
    middleware = CatchExceptionsMiddleware(app, custom_logger=custom)
    assert middleware.logger is custom


# ---------------------------------------------------------------------------
# safe_serialize
# ---------------------------------------------------------------------------


def test_dict_is_serialized_recursively():
    """Verifica que um dicionario e serializado recursivamente mantendo sua estrutura."""
    middleware = _make_middleware()
    result = middleware.safe_serialize({"key": "value", "nested": {"a": 1}})
    assert result == {"key": "value", "nested": {"a": 1}}


def test_list_is_serialized_recursively():
    """Verifica que uma lista e serializada recursivamente mantendo seus elementos."""
    middleware = _make_middleware()
    result = middleware.safe_serialize([1, "two", {"three": 3}])
    assert result == [1, "two", {"three": 3}]


def test_tuple_is_serialized_as_list():
    """Verifica que uma tupla e serializada como lista."""
    middleware = _make_middleware()
    result = middleware.safe_serialize((1, 2, 3))
    assert result == [1, 2, 3]


def test_primitive_json_serializable_returned_as_is():
    """Verifica que valores primitivos serializaveis em JSON sao retornados sem alteracao."""
    middleware = _make_middleware()
    assert middleware.safe_serialize(42) == 42
    assert middleware.safe_serialize(3.14) == 3.14
    assert middleware.safe_serialize("hello") == "hello"
    assert middleware.safe_serialize(True) is True
    assert middleware.safe_serialize(None) is None


def test_non_json_serializable_value_becomes_string():
    """Verifica que valores nao serializaveis em JSON sem __dict__ sao convertidos para string.

    Um conjunto (set) nao possui __dict__ (hasattr retorna False) e nao e serializavel em JSON,
    portanto safe_serialize cai no ramo de fallback e retorna str().
    """
    middleware = _make_middleware()
    result = middleware.safe_serialize({1, 2, 3})
    assert isinstance(result, str)


def test_object_with_dict_is_serialized():
    """Verifica que objetos com __dict__ sao serializados usando seus atributos."""
    middleware = _make_middleware()

    class Simple:
        def __init__(self):
            self.x = 1
            self.y = "two"

    result = middleware.safe_serialize(Simple())
    assert result == {"x": 1, "y": "two"}


def test_nested_object_inside_dict():
    """Verifica que objetos aninhados dentro de dicionarios sao serializados corretamente."""
    middleware = _make_middleware()

    class Inner:
        def __init__(self):
            self.value = 99

    result = middleware.safe_serialize({"inner": Inner()})
    assert result == {"inner": {"value": 99}}


def test_object_whose_dict_iteration_raises_returns_str():
    """Verifica que safe_serialize retorna str() quando a iteracao de __dict__ levanta excecao."""

    middleware = _make_middleware()

    class Problematic:
        @property
        def __dict__(self):
            return _RaisingMapping()

    class _RaisingMapping:
        def items(self):
            raise RuntimeError("cannot iterate")

    obj = Problematic()
    result = middleware.safe_serialize(obj)
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# dispatch - excecoes conhecidas
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "exc_class,expected_status",
    [
        (ProviderNotConfiguredError, 503),
        (IngestionError, 500),
        (SearchError, 500),
        (VectorStoreError, 500),
    ],
)
def test_known_exception_returns_correct_status_code(exc_class, expected_status):
    """Verifica que excecoes conhecidas retornam o codigo HTTP esperado conforme o mapa."""
    client = TestClient(_build_app(raise_exc=exc_class("test error")))
    response = client.get("/trigger")
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "exc_class",
    [ProviderNotConfiguredError, IngestionError, SearchError, VectorStoreError],
)
def test_known_exception_response_contains_error_message(exc_class):
    """Verifica que a resposta de excecoes conhecidas contem a mensagem de erro original."""
    client = TestClient(_build_app(raise_exc=exc_class("something went wrong")))
    response = client.get("/trigger")
    body = response.json()
    assert "something went wrong" in body["error"]


@pytest.mark.parametrize(
    "exc_class",
    [ProviderNotConfiguredError, IngestionError, SearchError, VectorStoreError],
)
def test_known_exception_response_contains_error_type(exc_class):
    """Verifica que a resposta de excecoes conhecidas contem o tipo da excecao no campo error_type."""
    client = TestClient(_build_app(raise_exc=exc_class("msg")))
    response = client.get("/trigger")
    body = response.json()
    assert body["error_type"] == exc_class.__name__


@pytest.mark.parametrize(
    "exc_class",
    [ProviderNotConfiguredError, IngestionError, SearchError, VectorStoreError],
)
def test_known_exception_response_contains_timestamp(exc_class):
    """Verifica que a resposta de excecoes conhecidas contem um timestamp em formato ISO."""
    client = TestClient(_build_app(raise_exc=exc_class("msg")))
    response = client.get("/trigger")
    body = response.json()
    assert "timestamp" in body
    datetime.fromisoformat(body["timestamp"])


@pytest.mark.parametrize(
    "exc_class",
    [ProviderNotConfiguredError, IngestionError, SearchError, VectorStoreError],
)
def test_known_exception_response_contains_path(exc_class):
    """Verifica que a resposta de excecoes conhecidas contem o caminho da requisicao."""
    client = TestClient(_build_app(raise_exc=exc_class("msg")))
    response = client.get("/trigger")
    body = response.json()
    assert body["request_path"] == "/trigger"


@pytest.mark.parametrize(
    "exc_class",
    [ProviderNotConfiguredError, IngestionError, SearchError, VectorStoreError],
)
def test_known_exception_response_contains_method(exc_class):
    """Verifica que a resposta de excecoes conhecidas contem o metodo HTTP da requisicao."""
    client = TestClient(_build_app(raise_exc=exc_class("msg")))
    response = client.get("/trigger")
    body = response.json()
    assert body["request_method"] == "GET"


@pytest.mark.parametrize(
    "exc_class",
    [ProviderNotConfiguredError, IngestionError, SearchError, VectorStoreError],
)
def test_known_exception_logs_details(exc_class):
    """Verifica que excecoes conhecidas registram blocos de EXCEPTION DETAILS e END EXCEPTION DETAILS no logger."""
    mock_logger = MagicMock()
    client = TestClient(
        _build_app(raise_exc=exc_class("msg"), custom_logger=mock_logger)
    )
    client.get("/trigger")

    error_calls = [c.args[0] for c in mock_logger.error.call_args_list]
    assert any("EXCEPTION DETAILS" in msg for msg in error_calls)
    assert any("END EXCEPTION DETAILS" in msg for msg in error_calls)


def test_known_exception_does_not_include_traceback_in_body():
    """Verifica que a resposta de excecoes conhecidas nao expoe o traceback no corpo da resposta."""
    client = TestClient(_build_app(raise_exc=IngestionError("no traceback")))
    response = client.get("/trigger")
    body = response.json()
    assert "traceback" not in body


# ---------------------------------------------------------------------------
# dispatch - excecoes genericas
# ---------------------------------------------------------------------------


def test_generic_exception_returns_500():
    """Verifica que excecoes genericas (nao mapeadas) retornam status HTTP 500."""
    client = TestClient(_build_app(raise_exc=RuntimeError("generic")))
    response = client.get("/trigger")
    assert response.status_code == 500


def test_generic_exception_response_contains_error_message():
    """Verifica que a resposta de excecoes genericas contem a mensagem de erro original."""
    client = TestClient(_build_app(raise_exc=ValueError("bad value")))
    response = client.get("/trigger")
    body = response.json()
    assert "bad value" in body["error"]


def test_generic_exception_response_contains_error_type():
    """Verifica que a resposta de excecoes genericas contem o tipo da excecao no campo error_type."""
    client = TestClient(_build_app(raise_exc=RuntimeError("oops")))
    response = client.get("/trigger")
    body = response.json()
    assert body["error_type"] == "RuntimeError"


def test_generic_exception_response_contains_traceback():
    """Verifica que a resposta de excecoes genericas inclui o traceback com o nome da excecao."""
    client = TestClient(_build_app(raise_exc=RuntimeError("oops")))
    response = client.get("/trigger")
    body = response.json()
    assert "traceback" in body
    assert "RuntimeError" in body["traceback"]


def test_generic_exception_response_contains_timestamp():
    """Verifica que a resposta de excecoes genericas contem um timestamp em formato ISO."""
    client = TestClient(_build_app(raise_exc=RuntimeError("oops")))
    response = client.get("/trigger")
    body = response.json()
    assert "timestamp" in body
    datetime.fromisoformat(body["timestamp"])


def test_generic_exception_response_contains_path():
    """Verifica que a resposta de excecoes genericas contem o caminho da requisicao."""
    client = TestClient(_build_app(raise_exc=RuntimeError("oops")))
    response = client.get("/trigger")
    body = response.json()
    assert body["request_path"] == "/trigger"


def test_generic_exception_response_contains_method():
    """Verifica que a resposta de excecoes genericas contem o metodo HTTP da requisicao."""
    client = TestClient(_build_app(raise_exc=RuntimeError("oops")))
    response = client.get("/trigger")
    body = response.json()
    assert body["request_method"] == "GET"


def test_generic_exception_logs_full_traceback():
    """Verifica que excecoes genericas registram o traceback completo no logger."""
    mock_logger = MagicMock()
    client = TestClient(
        _build_app(raise_exc=RuntimeError("oops"), custom_logger=mock_logger)
    )
    client.get("/trigger")

    error_calls = mock_logger.error.call_args_list
    logged_messages = [c.args[0] for c in error_calls]
    assert any("Full Traceback" in msg for msg in logged_messages)


# ---------------------------------------------------------------------------
# dispatch - ValidationError
# ---------------------------------------------------------------------------


def test_validation_error_returns_422():
    """Verifica que ResponseValidationError gerada por retorno invalido de rota resulta em status 422."""
    from pydantic import BaseModel

    app = FastAPI()
    app.add_middleware(CatchExceptionsMiddleware)

    class StrictResponse(BaseModel):
        value: int

    @app.get("/bad-response", response_model=StrictResponse)
    def bad_response():
        return {"value": "not-an-int"}

    client = TestClient(app)
    response = client.get("/bad-response")
    assert response.status_code == 422


def test_validation_error_response_contains_detail():
    """Verifica que a resposta de ValidationError contem o campo detail com valor 'Validation Error'."""
    from pydantic import BaseModel

    app = FastAPI()
    app.add_middleware(CatchExceptionsMiddleware)

    class StrictResponse(BaseModel):
        value: int

    @app.get("/bad-response", response_model=StrictResponse)
    def bad_response():
        return {"value": "not-an-int"}

    client = TestClient(app)
    response = client.get("/bad-response")
    body = response.json()
    assert body["detail"] == "Validation Error"


def test_validation_error_response_contains_timestamp():
    """Verifica que a resposta de ValidationError contem um timestamp em formato ISO valido."""
    from pydantic import BaseModel

    app = FastAPI()
    app.add_middleware(CatchExceptionsMiddleware)

    class StrictResponse(BaseModel):
        value: int

    @app.get("/bad-response", response_model=StrictResponse)
    def bad_response():
        return {"value": "not-an-int"}

    client = TestClient(app)
    response = client.get("/bad-response")
    body = response.json()
    assert "timestamp" in body
    datetime.fromisoformat(body["timestamp"])


def test_validation_error_logs_error():
    """Verifica que ValidationError e registrada no logger com a mensagem 'Validation Error'."""
    from pydantic import BaseModel

    mock_logger = MagicMock()
    app = FastAPI()
    app.add_middleware(CatchExceptionsMiddleware, custom_logger=mock_logger)

    class StrictResponse(BaseModel):
        value: int

    @app.get("/bad-response", response_model=StrictResponse)
    def bad_response():
        return {"value": "not-an-int"}

    client = TestClient(app)
    client.get("/bad-response")

    error_calls = [c.args[0] for c in mock_logger.error.call_args_list]
    assert any("Validation Error" in msg for msg in error_calls)


# ---------------------------------------------------------------------------
# dispatch - requisicao bem-sucedida
# ---------------------------------------------------------------------------


def test_successful_request_passes_through():
    """Verifica que requisicoes sem excecao passam pelo middleware com status 200 e resposta correta."""
    client = TestClient(_build_app())
    response = client.get("/trigger")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# _create_error_response
# ---------------------------------------------------------------------------


def test_returns_json_response_with_correct_status():
    """Verifica que _create_error_response retorna um JSONResponse com o status code informado."""
    from fastapi.responses import JSONResponse

    result = CatchExceptionsMiddleware._create_error_response(
        status_code=503, content={"error": "service unavailable"}
    )
    assert isinstance(result, JSONResponse)
    assert result.status_code == 503


def test_returns_json_response_with_correct_content():
    """Verifica que _create_error_response retorna um JSONResponse com o conteudo informado."""
    result = CatchExceptionsMiddleware._create_error_response(
        status_code=500, content={"error": "server error", "code": 42}
    )
    body = json.loads(result.body)
    assert body["error"] == "server error"
    assert body["code"] == 42


# ---------------------------------------------------------------------------
# _log_exception_details
# ---------------------------------------------------------------------------


def test_log_exception_details_without_traceback():
    """Verifica que _log_exception_details registra os blocos EXCEPTION DETAILS sem traceback quando ele e None."""
    mock_logger = MagicMock()
    app = FastAPI()
    middleware = CatchExceptionsMiddleware(app, custom_logger=mock_logger)

    mock_request = MagicMock()
    mock_request.method = "POST"
    mock_request.url.path = "/api/test"
    mock_request.query_params = {}

    middleware._log_exception_details(
        request=mock_request,
        exc=ValueError("test error"),
        error_time="2024-01-01T00:00:00+00:00",
        error_traceback=None,
    )

    error_calls = [c.args[0] for c in mock_logger.error.call_args_list]
    assert any("EXCEPTION DETAILS" in msg for msg in error_calls)
    assert any("END EXCEPTION DETAILS" in msg for msg in error_calls)
    assert not any("Full Traceback" in msg for msg in error_calls)


def test_log_exception_details_with_traceback():
    """Verifica que _log_exception_details registra o traceback completo quando ele e fornecido."""
    mock_logger = MagicMock()
    app = FastAPI()
    middleware = CatchExceptionsMiddleware(app, custom_logger=mock_logger)

    mock_request = MagicMock()
    mock_request.method = "GET"
    mock_request.url.path = "/api/test"
    mock_request.query_params = {}

    middleware._log_exception_details(
        request=mock_request,
        exc=RuntimeError("oops"),
        error_time="2024-01-01T00:00:00+00:00",
        error_traceback="Traceback (most recent call last):\n  ...",
    )

    error_calls = [c.args[0] for c in mock_logger.error.call_args_list]
    assert any("Full Traceback" in msg for msg in error_calls)
