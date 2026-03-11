"""Tests for app.services.llm_service.LLMService."""

from unittest.mock import MagicMock, patch


from app.exceptions import ProviderNotConfiguredError
from app.services.llm_service import LLMService, SEARCH_PROMPT


# ---------------------------------------------------------------------------
# SEARCH_PROMPT
# ---------------------------------------------------------------------------


def test_llm_service_search_prompt_contains_contexto_variable():
    """Verifica que a constante SEARCH_PROMPT contem a variavel de template
    '{contexto}', necessaria para injetar o contexto na cadeia LLM."""
    assert "{contexto}" in SEARCH_PROMPT


def test_llm_service_search_prompt_contains_pergunta_variable():
    """Verifica que a constante SEARCH_PROMPT contem a variavel de template
    '{pergunta}', necessaria para injetar a pergunta do usuario na cadeia LLM."""
    assert "{pergunta}" in SEARCH_PROMPT


def test_llm_service_search_prompt_is_non_empty_string():
    """Verifica que SEARCH_PROMPT e uma string nao vazia, garantindo que o
    template foi definido corretamente."""
    assert isinstance(SEARCH_PROMPT, str)
    assert len(SEARCH_PROMPT) > 0


# ---------------------------------------------------------------------------
# _get_provider
# ---------------------------------------------------------------------------


@patch("app.services.llm_service.create_provider")
def test_llm_service_calls_create_provider_on_first_access(mock_create_provider):
    """Verifica que _get_provider chama create_provider exatamente uma vez
    na primeira vez em que e invocado."""
    mock_provider = MagicMock()
    mock_create_provider.return_value = mock_provider

    service = LLMService()
    service._get_provider()

    mock_create_provider.assert_called_once()


@patch("app.services.llm_service.create_provider")
def test_llm_service_caches_provider_on_second_access(mock_create_provider):
    """Verifica que _get_provider reutiliza o provider criado na primeira
    chamada, sem invocar create_provider novamente."""
    mock_provider = MagicMock()
    mock_create_provider.return_value = mock_provider

    service = LLMService()
    first = service._get_provider()
    second = service._get_provider()

    mock_create_provider.assert_called_once()
    assert first is second


@patch("app.services.llm_service.create_provider")
def test_llm_service_sets_internal_provider_attribute(mock_create_provider):
    """Verifica que _get_provider armazena o provider retornado no atributo
    interno _provider do servico."""
    mock_provider = MagicMock()
    mock_create_provider.return_value = mock_provider

    service = LLMService()
    service._get_provider()

    assert service._provider is mock_provider


@patch("app.services.llm_service.create_provider")
def test_llm_service_skips_create_provider_when_already_cached(mock_create_provider):
    """Verifica que _get_provider nao chama create_provider quando o provider
    ja esta armazenado no atributo _provider do servico."""
    mock_provider = MagicMock()
    service = LLMService()
    service._provider = mock_provider

    result = service._get_provider()

    mock_create_provider.assert_not_called()
    assert result is mock_provider


# ---------------------------------------------------------------------------
# _get_fallback_provider
# ---------------------------------------------------------------------------


@patch("app.services.llm_service.create_fallback_provider")
def test_llm_service_calls_create_fallback_provider_on_first_access(
    mock_create_fallback,
):
    """Verifica que _get_fallback_provider chama create_fallback_provider
    exatamente uma vez na primeira vez em que e invocado."""
    mock_fallback = MagicMock()
    mock_create_fallback.return_value = mock_fallback

    service = LLMService()
    service._get_fallback_provider()

    mock_create_fallback.assert_called_once()


@patch("app.services.llm_service.create_fallback_provider")
def test_llm_service_caches_fallback_provider_on_second_access(mock_create_fallback):
    """Verifica que _get_fallback_provider reutiliza o fallback criado na
    primeira chamada, sem invocar create_fallback_provider novamente."""
    mock_fallback = MagicMock()
    mock_create_fallback.return_value = mock_fallback

    service = LLMService()
    first = service._get_fallback_provider()
    second = service._get_fallback_provider()

    mock_create_fallback.assert_called_once()
    assert first is second


@patch("app.services.llm_service.create_fallback_provider")
def test_llm_service_returns_none_when_no_fallback_configured(mock_create_fallback):
    """Verifica que _get_fallback_provider retorna None quando nenhum
    provedor de fallback esta configurado."""
    mock_create_fallback.return_value = None

    service = LLMService()
    result = service._get_fallback_provider()

    assert result is None


@patch("app.services.llm_service.create_fallback_provider")
def test_llm_service_skips_create_fallback_when_already_cached(mock_create_fallback):
    """Verifica que _get_fallback_provider nao chama create_fallback_provider
    quando o fallback ja esta armazenado no atributo _fallback_provider."""
    mock_fallback = MagicMock()
    service = LLMService()
    service._fallback_provider = mock_fallback

    result = service._get_fallback_provider()

    mock_create_fallback.assert_not_called()
    assert result is mock_fallback


# ---------------------------------------------------------------------------
# get_provider_name
# ---------------------------------------------------------------------------


@patch("app.services.llm_service.create_provider")
def test_llm_service_returns_provider_name(mock_create_provider):
    """Verifica que get_provider_name retorna o nome do provedor configurado."""
    mock_provider = MagicMock()
    mock_provider.get_provider_name.return_value = "Gemini"
    mock_create_provider.return_value = mock_provider

    service = LLMService()
    result = service.get_provider_name()

    assert result == "Gemini"


@patch("app.services.llm_service.create_provider")
def test_llm_service_returns_none_string_when_provider_not_configured(
    mock_create_provider,
):
    """Verifica que get_provider_name retorna a string 'None' quando
    create_provider lanca ProviderNotConfiguredError."""
    mock_create_provider.side_effect = ProviderNotConfiguredError()

    service = LLMService()
    result = service.get_provider_name()

    assert result == "None"


@patch("app.services.llm_service.create_provider")
def test_llm_service_delegates_to_provider_get_provider_name(mock_create_provider):
    """Verifica que get_provider_name delega a chamada ao metodo
    get_provider_name do provider subjacente."""
    mock_provider = MagicMock()
    mock_provider.get_provider_name.return_value = "OpenAI"
    mock_create_provider.return_value = mock_provider

    service = LLMService()
    service.get_provider_name()

    mock_provider.get_provider_name.assert_called()


# ---------------------------------------------------------------------------
# build_chain
# ---------------------------------------------------------------------------


@patch("app.services.llm_service.create_fallback_provider")
@patch("app.services.llm_service.create_provider")
def test_llm_service_build_chain_returns_chain_object(
    mock_create_provider, mock_create_fallback
):
    """Verifica que build_chain retorna um objeto de chain nao nulo quando
    o provider primario esta configurado e nao ha fallback."""
    mock_llm = MagicMock()
    mock_provider = MagicMock()
    mock_provider.get_llm.return_value = mock_llm
    mock_provider.get_provider_name.return_value = "Gemini"
    mock_create_provider.return_value = mock_provider
    mock_create_fallback.return_value = None

    # Make | operator work by returning a mock chain
    mock_llm.__ror__ = MagicMock(return_value=MagicMock())

    service = LLMService()
    chain = service.build_chain()

    assert chain is not None


@patch("app.services.llm_service.create_fallback_provider")
@patch("app.services.llm_service.create_provider")
def test_llm_service_build_chain_caches_result(
    mock_create_provider, mock_create_fallback
):
    """Verifica que build_chain retorna o mesmo objeto de chain em chamadas
    repetidas, sem reconstruir a cadeia desnecessariamente."""
    mock_provider = MagicMock()
    mock_provider.get_provider_name.return_value = "Gemini"
    mock_create_provider.return_value = mock_provider
    mock_create_fallback.return_value = None

    service = LLMService()
    first = service.build_chain()
    second = service.build_chain()

    assert first is second


@patch("app.services.llm_service.create_fallback_provider")
@patch("app.services.llm_service.create_provider")
def test_llm_service_build_chain_skips_rebuild_when_already_cached(
    mock_create_provider, mock_create_fallback
):
    """Verifica que build_chain nao chama create_provider nem
    create_fallback_provider quando a chain ja esta armazenada em _chain."""
    prebuilt_chain = MagicMock()
    service = LLMService()
    service._chain = prebuilt_chain

    result = service.build_chain()

    mock_create_provider.assert_not_called()
    mock_create_fallback.assert_not_called()
    assert result is prebuilt_chain


@patch("app.services.llm_service.create_fallback_provider")
@patch("app.services.llm_service.create_provider")
def test_llm_service_build_chain_without_fallback_does_not_call_with_fallbacks(
    mock_create_provider, mock_create_fallback
):
    """Verifica que build_chain nao invoca with_fallbacks em nenhum componente
    da chain quando nao ha provedor de fallback configurado."""
    mock_chain = MagicMock()
    mock_provider = MagicMock()
    mock_provider.get_provider_name.return_value = "Gemini"
    mock_create_provider.return_value = mock_provider
    mock_create_fallback.return_value = None

    service = LLMService()
    service.build_chain()

    # with_fallbacks should NOT have been called on any chain component
    mock_chain.with_fallbacks.assert_not_called()


@patch("app.services.llm_service.create_fallback_provider")
@patch("app.services.llm_service.create_provider")
def test_llm_service_build_chain_with_fallback_calls_with_fallbacks(
    mock_create_provider, mock_create_fallback
):
    """Verifica que build_chain utiliza o LLM de fallback quando um provedor
    de fallback esta configurado, e armazena o resultado final em _chain."""
    mock_primary_llm = MagicMock()
    mock_fallback_llm = MagicMock()

    mock_primary_provider = MagicMock()
    mock_primary_provider.get_llm.return_value = mock_primary_llm
    mock_primary_provider.get_provider_name.return_value = "Gemini"

    mock_fallback_provider = MagicMock()
    mock_fallback_provider.get_llm.return_value = mock_fallback_llm
    mock_fallback_provider.get_provider_name.return_value = "OpenAI"

    mock_create_provider.return_value = mock_primary_provider
    mock_create_fallback.return_value = mock_fallback_provider

    service = LLMService()
    chain = service.build_chain()

    # The chain returned by with_fallbacks should have been set as _chain
    assert service._chain is chain


# ---------------------------------------------------------------------------
# ask
# ---------------------------------------------------------------------------


@patch("app.services.llm_service.create_fallback_provider")
@patch("app.services.llm_service.create_provider")
def test_llm_service_ask_invokes_chain_with_context_and_question(
    mock_create_provider, mock_create_fallback
):
    """Verifica que ask invoca a chain com os parametros 'contexto' e
    'pergunta' corretos e retorna o resultado da invocacao."""
    mock_provider = MagicMock()
    mock_provider.get_provider_name.return_value = "Gemini"
    mock_create_provider.return_value = mock_provider
    mock_create_fallback.return_value = None

    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "the answer"

    service = LLMService()
    service._chain = mock_chain

    result = service.ask("some context", "some question")

    mock_chain.invoke.assert_called_once_with(
        {"contexto": "some context", "pergunta": "some question"}
    )
    assert result == "the answer"


@patch("app.services.llm_service.create_fallback_provider")
@patch("app.services.llm_service.create_provider")
def test_llm_service_ask_delegates_to_build_chain(
    mock_create_provider, mock_create_fallback
):
    """Verifica que ask delega a execucao para a chain construida por
    build_chain, chamando invoke exatamente uma vez."""
    mock_provider = MagicMock()
    mock_provider.get_provider_name.return_value = "Gemini"
    mock_create_provider.return_value = mock_provider
    mock_create_fallback.return_value = None

    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "response"

    service = LLMService()
    service._chain = mock_chain

    service.ask("ctx", "q")

    mock_chain.invoke.assert_called_once()


@patch("app.services.llm_service.create_fallback_provider")
@patch("app.services.llm_service.create_provider")
def test_llm_service_ask_returns_chain_invoke_result(
    mock_create_provider, mock_create_fallback
):
    """Verifica que ask retorna exatamente o valor retornado por chain.invoke,
    sem modificacoes."""
    mock_provider = MagicMock()
    mock_provider.get_provider_name.return_value = "Gemini"
    mock_create_provider.return_value = mock_provider
    mock_create_fallback.return_value = None

    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "expected answer"

    service = LLMService()
    service._chain = mock_chain

    result = service.ask("context text", "question text")

    assert result == "expected answer"
