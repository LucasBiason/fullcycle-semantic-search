"""Tests for app.schemas.search - SearchRequest, SearchResponse."""

import pytest
from pydantic import ValidationError

from app.schemas.search import SearchRequest, SearchResponse


# ---------------------------------------------------------------------------
# SearchRequest
# ---------------------------------------------------------------------------


def test_search_request_valid_question_and_default_k():
    """Verifica que SearchRequest aceita uma pergunta valida e usa k=20 como padrao."""
    req = SearchRequest(question="What is AI?")
    assert req.question == "What is AI?"
    assert req.k == 20


def test_search_request_valid_question_with_custom_k():
    """Verifica que SearchRequest aceita um valor customizado para k."""
    req = SearchRequest(question="Tell me about ML", k=10)
    assert req.k == 10


def test_search_request_question_min_length_boundary_passes():
    """Verifica que uma pergunta com exatamente 3 caracteres e aceita (limite minimo)."""
    req = SearchRequest(question="abc")
    assert req.question == "abc"


def test_search_request_question_below_min_length_raises():
    """Verifica que uma pergunta com menos de 3 caracteres levanta ValidationError."""
    with pytest.raises(ValidationError):
        SearchRequest(question="ab")


def test_search_request_question_max_length_boundary_passes():
    """Verifica que uma pergunta com exatamente 5000 caracteres e aceita (limite maximo)."""
    long_question = "a" * 5000
    req = SearchRequest(question=long_question)
    assert len(req.question) == 5000


def test_search_request_question_above_max_length_raises():
    """Verifica que uma pergunta com mais de 5000 caracteres levanta ValidationError."""
    with pytest.raises(ValidationError):
        SearchRequest(question="a" * 5001)


def test_search_request_question_required_raises_when_missing():
    """Verifica que omitir o campo question levanta ValidationError."""
    with pytest.raises(ValidationError):
        SearchRequest()


def test_search_request_k_minimum_boundary_passes():
    """Verifica que k=1 e aceito como valor minimo valido."""
    req = SearchRequest(question="Valid question here", k=1)
    assert req.k == 1


def test_search_request_k_below_minimum_raises():
    """Verifica que k=0 levanta ValidationError por estar abaixo do minimo permitido."""
    with pytest.raises(ValidationError):
        SearchRequest(question="Valid question here", k=0)


def test_search_request_k_maximum_boundary_passes():
    """Verifica que k=50 e aceito como valor maximo valido."""
    req = SearchRequest(question="Valid question here", k=50)
    assert req.k == 50


def test_search_request_k_above_maximum_raises():
    """Verifica que k=51 levanta ValidationError por exceder o valor maximo permitido."""
    with pytest.raises(ValidationError):
        SearchRequest(question="Valid question here", k=51)


# ---------------------------------------------------------------------------
# SearchResponse
# ---------------------------------------------------------------------------


def test_search_response_construction_with_answer():
    """Verifica que SearchResponse e construida corretamente com o campo answer."""
    response = SearchResponse(answer="The answer is 42")
    assert response.answer == "The answer is 42"


def test_search_response_serialization():
    """Verifica que SearchResponse serializa corretamente para dicionario via model_dump."""
    response = SearchResponse(answer="Test answer")
    data = response.model_dump()
    assert data == {"answer": "Test answer"}


def test_search_response_answer_is_required():
    """Verifica que omitir o campo answer levanta ValidationError."""
    with pytest.raises(ValidationError):
        SearchResponse()
