"""Tests for app.services.embedding_service.EmbeddingService."""

from unittest.mock import MagicMock, patch


from app.exceptions import ProviderNotConfiguredError
from app.services.embedding_service import EmbeddingService


# ---------------------------------------------------------------------------
# _get_provider
# ---------------------------------------------------------------------------


@patch("app.services.embedding_service.create_provider")
def test_embedding_service_calls_create_provider_on_first_access(mock_create_provider):
    """Verifica que _get_provider chama create_provider exatamente uma vez
    na primeira vez em que e invocado."""
    mock_provider = MagicMock()
    mock_create_provider.return_value = mock_provider

    service = EmbeddingService()
    service._get_provider()

    mock_create_provider.assert_called_once()


@patch("app.services.embedding_service.create_provider")
def test_embedding_service_caches_provider_on_second_access(mock_create_provider):
    """Verifica que _get_provider reutiliza o provider criado na primeira
    chamada, sem invocar create_provider novamente."""
    mock_provider = MagicMock()
    mock_create_provider.return_value = mock_provider

    service = EmbeddingService()
    first = service._get_provider()
    second = service._get_provider()

    mock_create_provider.assert_called_once()
    assert first is second


@patch("app.services.embedding_service.create_provider")
def test_embedding_service_returns_provider_from_create_provider(mock_create_provider):
    """Verifica que _get_provider retorna exatamente o objeto retornado por
    create_provider."""
    mock_provider = MagicMock()
    mock_create_provider.return_value = mock_provider

    service = EmbeddingService()
    result = service._get_provider()

    assert result is mock_provider


@patch("app.services.embedding_service.create_provider")
def test_embedding_service_sets_internal_provider_attribute(mock_create_provider):
    """Verifica que _get_provider armazena o provider retornado no atributo
    interno _provider do servico."""
    mock_provider = MagicMock()
    mock_create_provider.return_value = mock_provider

    service = EmbeddingService()
    service._get_provider()

    assert service._provider is mock_provider


@patch("app.services.embedding_service.create_provider")
def test_embedding_service_skips_create_provider_when_already_cached(
    mock_create_provider,
):
    """Verifica que _get_provider nao chama create_provider quando o provider
    ja esta armazenado no atributo _provider do servico."""
    mock_provider = MagicMock()
    service = EmbeddingService()
    service._provider = mock_provider

    result = service._get_provider()

    mock_create_provider.assert_not_called()
    assert result is mock_provider


# ---------------------------------------------------------------------------
# get_embeddings
# ---------------------------------------------------------------------------


@patch("app.services.embedding_service.create_provider")
def test_embedding_service_delegates_to_provider_get_embeddings(mock_create_provider):
    """Verifica que get_embeddings delega a chamada ao metodo get_embeddings
    do provider e retorna o resultado obtido."""
    mock_embeddings = MagicMock()
    mock_provider = MagicMock()
    mock_provider.get_embeddings.return_value = mock_embeddings
    mock_create_provider.return_value = mock_provider

    service = EmbeddingService()
    result = service.get_embeddings()

    mock_provider.get_embeddings.assert_called_once()
    assert result is mock_embeddings


@patch("app.services.embedding_service.create_provider")
def test_embedding_service_returns_same_embeddings_on_repeated_calls(
    mock_create_provider,
):
    """Verifica que get_embeddings retorna o mesmo objeto em chamadas
    repetidas, refletindo o comportamento de cache do provider."""
    mock_embeddings = MagicMock()
    mock_provider = MagicMock()
    mock_provider.get_embeddings.return_value = mock_embeddings
    mock_create_provider.return_value = mock_provider

    service = EmbeddingService()
    first = service.get_embeddings()
    second = service.get_embeddings()

    assert first is second


# ---------------------------------------------------------------------------
# get_provider_name
# ---------------------------------------------------------------------------


@patch("app.services.embedding_service.create_provider")
def test_embedding_service_returns_provider_name(mock_create_provider):
    """Verifica que get_provider_name retorna o nome do provedor configurado."""
    mock_provider = MagicMock()
    mock_provider.get_provider_name.return_value = "Gemini"
    mock_create_provider.return_value = mock_provider

    service = EmbeddingService()
    result = service.get_provider_name()

    assert result == "Gemini"


@patch("app.services.embedding_service.create_provider")
def test_embedding_service_returns_none_string_when_provider_not_configured(
    mock_create_provider,
):
    """Verifica que get_provider_name retorna a string 'None' quando
    create_provider lanca ProviderNotConfiguredError."""
    mock_create_provider.side_effect = ProviderNotConfiguredError()

    service = EmbeddingService()
    result = service.get_provider_name()

    assert result == "None"


@patch("app.services.embedding_service.create_provider")
def test_embedding_service_delegates_to_provider_get_provider_name(
    mock_create_provider,
):
    """Verifica que get_provider_name delega a chamada ao metodo
    get_provider_name do provider subjacente."""
    mock_provider = MagicMock()
    mock_provider.get_provider_name.return_value = "OpenAI"
    mock_create_provider.return_value = mock_provider

    service = EmbeddingService()
    service.get_provider_name()

    mock_provider.get_provider_name.assert_called()


@patch("app.services.embedding_service.create_provider")
def test_embedding_service_get_provider_name_after_cached_provider_does_not_call_create_again(
    mock_create_provider,
):
    """Verifica que get_provider_name nao chama create_provider uma segunda
    vez quando o provider ja foi cacheado via _get_provider, e retorna o
    nome corretamente."""
    mock_provider = MagicMock()
    mock_provider.get_provider_name.return_value = "Gemini"
    mock_create_provider.return_value = mock_provider

    service = EmbeddingService()
    # First call caches the provider
    service._get_provider()
    # Second call through get_provider_name should not call create_provider again
    name = service.get_provider_name()

    mock_create_provider.assert_called_once()
    assert name == "Gemini"
