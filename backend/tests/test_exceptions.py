"""Tests for app.exceptions - custom exception classes."""

import pytest

from app.exceptions import (
    IngestionError,
    ProviderNotConfiguredError,
    SearchError,
    VectorStoreError,
)


# --- ProviderNotConfiguredError ---


def test_provider_not_configured_error_is_exception_subclass():
    """Verifica que ProviderNotConfiguredError e subclasse de Exception."""
    assert issubclass(ProviderNotConfiguredError, Exception)


def test_provider_not_configured_error_default_message():
    """Verifica que a mensagem padrao de ProviderNotConfiguredError indica que nenhum provedor LLM foi configurado."""
    error = ProviderNotConfiguredError()
    assert (
        str(error)
        == "No LLM provider configured. Set GOOGLE_API_KEY or OPENAI_API_KEY."
    )


def test_provider_not_configured_error_custom_message():
    """Verifica que ProviderNotConfiguredError aceita e exibe uma mensagem customizada corretamente."""
    error = ProviderNotConfiguredError("Custom error message")
    assert str(error) == "Custom error message"


def test_provider_not_configured_error_can_be_raised_and_caught_as_exception():
    """Verifica que ProviderNotConfiguredError pode ser lancada e capturada como Exception generica."""
    with pytest.raises(Exception):
        raise ProviderNotConfiguredError()


def test_provider_not_configured_error_can_be_raised_and_caught_as_itself():
    """Verifica que ProviderNotConfiguredError pode ser lancada e capturada pelo seu proprio tipo."""
    with pytest.raises(ProviderNotConfiguredError):
        raise ProviderNotConfiguredError()


def test_provider_not_configured_error_default_message_mentions_api_keys():
    """Verifica que a mensagem padrao menciona GOOGLE_API_KEY e OPENAI_API_KEY."""
    with pytest.raises(ProviderNotConfiguredError) as exc_info:
        raise ProviderNotConfiguredError()
    assert "GOOGLE_API_KEY" in str(exc_info.value)
    assert "OPENAI_API_KEY" in str(exc_info.value)


# --- IngestionError ---


def test_ingestion_error_is_exception_subclass():
    """Verifica que IngestionError e subclasse de Exception."""
    assert issubclass(IngestionError, Exception)


def test_ingestion_error_can_be_raised_with_message():
    """Verifica que IngestionError pode ser lancada com uma mensagem de erro e que a mensagem e preservada."""
    with pytest.raises(IngestionError) as exc_info:
        raise IngestionError("PDF loading failed")
    assert str(exc_info.value) == "PDF loading failed"


def test_ingestion_error_can_be_raised_without_message():
    """Verifica que IngestionError pode ser lancada sem argumentos."""
    with pytest.raises(IngestionError):
        raise IngestionError()


def test_ingestion_error_can_be_caught_as_exception():
    """Verifica que IngestionError pode ser capturada como Exception generica."""
    with pytest.raises(Exception):
        raise IngestionError("error")


def test_ingestion_error_is_not_subclass_of_provider_error():
    """Verifica que IngestionError nao e subclasse de ProviderNotConfiguredError, garantindo hierarquia independente."""
    assert not issubclass(IngestionError, ProviderNotConfiguredError)


# --- SearchError ---


def test_search_error_is_exception_subclass():
    """Verifica que SearchError e subclasse de Exception."""
    assert issubclass(SearchError, Exception)


def test_search_error_can_be_raised_with_message():
    """Verifica que SearchError pode ser lancada com uma mensagem de erro e que a mensagem e preservada."""
    with pytest.raises(SearchError) as exc_info:
        raise SearchError("Search pipeline failed")
    assert str(exc_info.value) == "Search pipeline failed"


def test_search_error_can_be_raised_without_message():
    """Verifica que SearchError pode ser lancada sem argumentos."""
    with pytest.raises(SearchError):
        raise SearchError()


def test_search_error_can_be_caught_as_exception():
    """Verifica que SearchError pode ser capturada como Exception generica."""
    with pytest.raises(Exception):
        raise SearchError("error")


def test_search_error_is_independent_from_ingestion_error():
    """Verifica que SearchError nao e subclasse de IngestionError, garantindo que sao erros independentes."""
    assert not issubclass(SearchError, IngestionError)


# --- VectorStoreError ---


def test_vector_store_error_is_exception_subclass():
    """Verifica que VectorStoreError e subclasse de Exception."""
    assert issubclass(VectorStoreError, Exception)


def test_vector_store_error_can_be_raised_with_message():
    """Verifica que VectorStoreError pode ser lancada com uma mensagem de erro e que a mensagem e preservada."""
    with pytest.raises(VectorStoreError) as exc_info:
        raise VectorStoreError("Vector store unavailable")
    assert str(exc_info.value) == "Vector store unavailable"


def test_vector_store_error_can_be_raised_without_message():
    """Verifica que VectorStoreError pode ser lancada sem argumentos."""
    with pytest.raises(VectorStoreError):
        raise VectorStoreError()


def test_vector_store_error_can_be_caught_as_exception():
    """Verifica que VectorStoreError pode ser capturada como Exception generica."""
    with pytest.raises(Exception):
        raise VectorStoreError("error")


def test_vector_store_error_is_independent_from_other_errors():
    """Verifica que VectorStoreError nao e subclasse de IngestionError, SearchError nem ProviderNotConfiguredError."""
    assert not issubclass(VectorStoreError, IngestionError)
    assert not issubclass(VectorStoreError, SearchError)
    assert not issubclass(VectorStoreError, ProviderNotConfiguredError)
