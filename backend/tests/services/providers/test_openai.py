"""Tests for app.services.providers.openai.OpenAIProvider."""

from unittest.mock import MagicMock, patch


from app.services.providers.openai import OpenAIProvider


# ---------------------------------------------------------------------------
# Inicializacao
# ---------------------------------------------------------------------------


def test_openai_provider_embeddings_starts_as_none():
    """Verifica que o atributo _embeddings do OpenAIProvider e None logo
    apos a instanciacao, antes de qualquer chamada a get_embeddings."""
    provider = OpenAIProvider()
    assert provider._embeddings is None


def test_openai_provider_llm_starts_as_none():
    """Verifica que o atributo _llm do OpenAIProvider e None logo apos a
    instanciacao, antes de qualquer chamada a get_llm."""
    provider = OpenAIProvider()
    assert provider._llm is None


# ---------------------------------------------------------------------------
# get_provider_name
# ---------------------------------------------------------------------------


def test_openai_provider_get_provider_name_returns_openai():
    """Verifica que get_provider_name retorna a string 'OpenAI', identificando
    corretamente o provedor."""
    provider = OpenAIProvider()
    assert provider.get_provider_name() == "OpenAI"


# ---------------------------------------------------------------------------
# get_embeddings
# ---------------------------------------------------------------------------


@patch("app.services.providers.openai.OpenAIEmbeddings")
def test_openai_provider_get_embeddings_initializes_on_first_call(mock_embeddings_cls):
    """Verifica que get_embeddings instancia OpenAIEmbeddings na primeira
    chamada e retorna a instancia criada."""
    mock_instance = MagicMock()
    mock_embeddings_cls.return_value = mock_instance

    provider = OpenAIProvider()
    result = provider.get_embeddings()

    mock_embeddings_cls.assert_called_once()
    assert result is mock_instance


@patch("app.services.providers.openai.OpenAIEmbeddings")
def test_openai_provider_get_embeddings_passes_model(mock_embeddings_cls):
    """Verifica que get_embeddings passa o argumento 'model' ao construtor
    de OpenAIEmbeddings."""
    mock_embeddings_cls.return_value = MagicMock()

    provider = OpenAIProvider()
    provider.get_embeddings()

    call_kwargs = mock_embeddings_cls.call_args.kwargs
    assert "model" in call_kwargs


@patch("app.services.providers.openai.OpenAIEmbeddings")
def test_openai_provider_get_embeddings_caches_instance_on_second_call(
    mock_embeddings_cls,
):
    """Verifica que get_embeddings reutiliza a instancia criada na primeira
    chamada, sem instanciar OpenAIEmbeddings novamente."""
    mock_instance = MagicMock()
    mock_embeddings_cls.return_value = mock_instance

    provider = OpenAIProvider()
    first = provider.get_embeddings()
    second = provider.get_embeddings()

    mock_embeddings_cls.assert_called_once()
    assert first is second


@patch("app.services.providers.openai.OpenAIEmbeddings")
def test_openai_provider_get_embeddings_sets_internal_attribute(mock_embeddings_cls):
    """Verifica que get_embeddings armazena a instancia criada no atributo
    interno _embeddings do provider."""
    mock_instance = MagicMock()
    mock_embeddings_cls.return_value = mock_instance

    provider = OpenAIProvider()
    provider.get_embeddings()

    assert provider._embeddings is mock_instance


# ---------------------------------------------------------------------------
# get_llm
# ---------------------------------------------------------------------------


@patch("app.services.providers.openai.ChatOpenAI")
def test_openai_provider_get_llm_initializes_on_first_call(mock_llm_cls):
    """Verifica que get_llm instancia ChatOpenAI na primeira chamada e
    retorna a instancia criada."""
    mock_instance = MagicMock()
    mock_llm_cls.return_value = mock_instance

    provider = OpenAIProvider()
    result = provider.get_llm()

    mock_llm_cls.assert_called_once()
    assert result is mock_instance


@patch("app.services.providers.openai.ChatOpenAI")
def test_openai_provider_get_llm_passes_model_and_temperature(mock_llm_cls):
    """Verifica que get_llm passa os argumentos 'model' e 'temperature'
    (igual a 0) ao construtor de ChatOpenAI."""
    mock_llm_cls.return_value = MagicMock()

    provider = OpenAIProvider()
    provider.get_llm()

    call_kwargs = mock_llm_cls.call_args.kwargs
    assert "model" in call_kwargs
    assert call_kwargs["temperature"] == 0


@patch("app.services.providers.openai.ChatOpenAI")
def test_openai_provider_get_llm_caches_instance_on_second_call(mock_llm_cls):
    """Verifica que get_llm reutiliza a instancia criada na primeira chamada,
    sem instanciar ChatOpenAI novamente."""
    mock_instance = MagicMock()
    mock_llm_cls.return_value = mock_instance

    provider = OpenAIProvider()
    first = provider.get_llm()
    second = provider.get_llm()

    mock_llm_cls.assert_called_once()
    assert first is second


@patch("app.services.providers.openai.ChatOpenAI")
def test_openai_provider_get_llm_sets_internal_attribute(mock_llm_cls):
    """Verifica que get_llm armazena a instancia criada no atributo interno
    _llm do provider."""
    mock_instance = MagicMock()
    mock_llm_cls.return_value = mock_instance

    provider = OpenAIProvider()
    provider.get_llm()

    assert provider._llm is mock_instance


@patch("app.services.providers.openai.ChatOpenAI")
@patch("app.services.providers.openai.OpenAIEmbeddings")
def test_openai_provider_embeddings_and_llm_are_independent(
    mock_embeddings_cls, mock_llm_cls
):
    """Verifica que as instancias de embeddings e LLM sao independentes entre
    si, ou seja, get_embeddings e get_llm retornam objetos distintos."""
    mock_emb = MagicMock()
    mock_llm = MagicMock()
    mock_embeddings_cls.return_value = mock_emb
    mock_llm_cls.return_value = mock_llm

    provider = OpenAIProvider()
    embeddings = provider.get_embeddings()
    llm = provider.get_llm()

    assert embeddings is mock_emb
    assert llm is mock_llm
    assert embeddings is not llm
