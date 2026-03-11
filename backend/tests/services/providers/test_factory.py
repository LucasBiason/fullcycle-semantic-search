"""Tests for factory functions in app.services.providers."""

from unittest.mock import MagicMock, patch

import pytest

from app.config import Settings
from app.exceptions import ProviderNotConfiguredError
from app.services.providers import create_fallback_provider, create_provider
from app.services.providers.gemini import GeminiProvider
from app.services.providers.openai import OpenAIProvider


# ---------------------------------------------------------------------------
# create_provider
# ---------------------------------------------------------------------------


def test_create_provider_returns_gemini_when_google_api_key_set():
    """Verifica que create_provider retorna GeminiProvider quando a chave
    do Google esta configurada e a do OpenAI esta vazia."""
    fake_settings = Settings(google_api_key="fake-google-key", openai_api_key="")
    with patch("app.services.providers.settings", fake_settings):
        provider = create_provider()
    assert isinstance(provider, GeminiProvider)


def test_create_provider_returns_openai_when_only_openai_api_key_set():
    """Verifica que create_provider retorna OpenAIProvider quando apenas a
    chave do OpenAI esta configurada."""
    fake_settings = Settings(google_api_key="", openai_api_key="fake-openai-key")
    with patch("app.services.providers.settings", fake_settings):
        provider = create_provider()
    assert isinstance(provider, OpenAIProvider)


def test_create_provider_raises_when_no_api_key_configured():
    """Verifica que create_provider lanca ProviderNotConfiguredError quando
    nenhuma chave de API esta configurada."""
    fake_settings = Settings(google_api_key="", openai_api_key="")
    with patch("app.services.providers.settings", fake_settings):
        with pytest.raises(ProviderNotConfiguredError):
            create_provider()


def test_create_provider_gemini_takes_priority_when_both_keys_set():
    """Verifica que o GeminiProvider tem prioridade sobre o OpenAIProvider
    quando ambas as chaves estao configuradas."""
    fake_settings = Settings(
        google_api_key="fake-google-key", openai_api_key="fake-openai-key"
    )
    with patch("app.services.providers.settings", fake_settings):
        provider = create_provider()
    assert isinstance(provider, GeminiProvider)


def test_create_provider_returns_new_instance_on_each_call():
    """Verifica que create_provider retorna uma nova instancia a cada chamada,
    sem reutilizar objetos anteriores."""
    fake_settings = Settings(google_api_key="fake-google-key", openai_api_key="")
    with patch("app.services.providers.settings", fake_settings):
        first = create_provider()
        second = create_provider()
    assert first is not second


def test_create_provider_error_message_contains_key_names():
    """Verifica que a mensagem de erro de ProviderNotConfiguredError menciona
    pelo menos uma das variaveis de ambiente esperadas."""
    fake_settings = Settings(google_api_key="", openai_api_key="")
    with patch("app.services.providers.settings", fake_settings):
        with pytest.raises(ProviderNotConfiguredError) as exc_info:
            create_provider()
    assert "GOOGLE_API_KEY" in str(exc_info.value) or "OPENAI_API_KEY" in str(
        exc_info.value
    )


# ---------------------------------------------------------------------------
# create_fallback_provider
# ---------------------------------------------------------------------------


def test_create_fallback_provider_returns_openai_when_gemini_is_primary():
    """Verifica que create_fallback_provider retorna OpenAIProvider como
    fallback quando o Gemini e o provedor primario e o OpenAI tambem esta
    configurado."""
    fake_settings = Settings(
        google_api_key="fake-google-key", openai_api_key="fake-openai-key"
    )
    with patch("app.services.providers.settings", fake_settings):
        fallback = create_fallback_provider()
    assert isinstance(fallback, OpenAIProvider)


def test_create_fallback_provider_returns_gemini_when_openai_is_primary():
    """Verifica que create_fallback_provider retorna GeminiProvider como
    fallback quando o provedor primario e o OpenAI. Este cenario e alcancado
    apenas via mock direto de settings, pois a logica padrao de Settings nao
    permite use_openai=True com google_api_key preenchida."""
    mock_settings = MagicMock()
    mock_settings.use_gemini = False
    mock_settings.use_openai = True
    mock_settings.google_api_key = "fake-google-key"
    mock_settings.openai_api_key = ""
    with patch("app.services.providers.settings", mock_settings):
        fallback = create_fallback_provider()
    assert isinstance(fallback, GeminiProvider)


def test_create_fallback_provider_returns_none_when_only_gemini_configured():
    """Verifica que create_fallback_provider retorna None quando somente o
    Gemini esta configurado e nao existe alternativa de fallback."""
    fake_settings = Settings(google_api_key="fake-google-key", openai_api_key="")
    with patch("app.services.providers.settings", fake_settings):
        fallback = create_fallback_provider()
    assert fallback is None


def test_create_fallback_provider_returns_none_when_only_openai_configured():
    """Verifica que create_fallback_provider retorna None quando somente o
    OpenAI esta configurado e nao existe alternativa de fallback."""
    fake_settings = Settings(google_api_key="", openai_api_key="fake-openai-key")
    with patch("app.services.providers.settings", fake_settings):
        fallback = create_fallback_provider()
    assert fallback is None


def test_create_fallback_provider_returns_none_when_no_keys_configured():
    """Verifica que create_fallback_provider retorna None quando nenhuma chave
    de API esta configurada."""
    fake_settings = Settings(google_api_key="", openai_api_key="")
    with patch("app.services.providers.settings", fake_settings):
        fallback = create_fallback_provider()
    assert fallback is None


def test_create_fallback_provider_returns_new_instance_on_each_call():
    """Verifica que create_fallback_provider retorna uma nova instancia a cada
    chamada, sem reutilizar objetos anteriores."""
    fake_settings = Settings(
        google_api_key="fake-google-key", openai_api_key="fake-openai-key"
    )
    with patch("app.services.providers.settings", fake_settings):
        first = create_fallback_provider()
        second = create_fallback_provider()
    assert first is not second
