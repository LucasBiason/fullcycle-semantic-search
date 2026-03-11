"""Tests for app.controllers.search_controller - SearchController."""

from unittest.mock import MagicMock, patch

from langchain_core.documents import Document

from app.controllers.search_controller import (
    CONTEXT_SEPARATOR,
    MAX_CONTEXT_LENGTH,
    NO_INFO_RESPONSE,
    SearchController,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_result(content: str, score: float = 0.9) -> tuple:
    """Build a (Document, score) tuple for use in test results."""
    doc = Document(page_content=content, metadata={"page": 1})
    return (doc, score)


def _make_controller() -> SearchController:
    """Return a SearchController with mocked services."""
    controller = SearchController.__new__(SearchController)
    controller.vector_store = MagicMock()
    controller.llm = MagicMock()
    return controller


# ---------------------------------------------------------------------------
# SearchController.__init__
# ---------------------------------------------------------------------------


@patch("app.controllers.search_controller.llm_service")
@patch("app.controllers.search_controller.vector_store_service")
def test_init_assigns_vector_store_service(mock_vector_store, mock_llm):
    """Verifica que __init__ atribui o vector_store_service ao atributo vector_store do controller."""
    controller = SearchController()
    assert controller.vector_store is mock_vector_store


@patch("app.controllers.search_controller.llm_service")
@patch("app.controllers.search_controller.vector_store_service")
def test_init_assigns_llm_service(mock_vector_store, mock_llm):
    """Verifica que __init__ atribui o llm_service ao atributo llm do controller."""
    controller = SearchController()
    assert controller.llm is mock_llm


# ---------------------------------------------------------------------------
# SearchController._build_context
# ---------------------------------------------------------------------------


def test_build_context_empty_results_returns_empty_string():
    """Verifica que _build_context retorna string vazia quando nao ha resultados."""
    result = SearchController._build_context([])
    assert result == ""


def test_build_context_single_result_returns_its_content():
    """Verifica que _build_context retorna apenas o conteudo do documento quando ha um unico resultado."""
    results = [_make_result("Only chunk")]
    context = SearchController._build_context(results)
    assert context == "Only chunk"


def test_build_context_multiple_results_joined_with_separator():
    """Verifica que _build_context concatena multiplos resultados usando CONTEXT_SEPARATOR."""
    results = [_make_result("First"), _make_result("Second")]
    context = SearchController._build_context(results)
    assert context == f"First{CONTEXT_SEPARATOR}Second"


def test_build_context_truncates_when_total_exceeds_max_length():
    """Verifica que _build_context trunca o contexto quando o total ultrapassa MAX_CONTEXT_LENGTH."""
    chunk = "a" * 3000
    results = [_make_result(chunk), _make_result(chunk)]
    context = SearchController._build_context(
        results, max_length=MAX_CONTEXT_LENGTH
    )
    assert len(context) <= MAX_CONTEXT_LENGTH + len(chunk)
    assert context.startswith("a" * 3000)


def test_build_context_first_chunk_always_included_even_if_it_exceeds_max():
    """Verifica que o primeiro chunk e sempre incluido no contexto, mesmo que exceda sozinho o MAX_CONTEXT_LENGTH."""
    huge_content = "x" * (MAX_CONTEXT_LENGTH + 1000)
    results = [_make_result(huge_content)]
    context = SearchController._build_context(results)
    assert context == huge_content


def test_build_context_second_chunk_excluded_when_would_exceed_max_length():
    """Verifica que o segundo chunk e excluido do contexto quando sua inclusao ultrapassaria o limite maximo."""
    chunk_a = "a" * (MAX_CONTEXT_LENGTH - 10)
    chunk_b = "b" * 100
    results = [_make_result(chunk_a), _make_result(chunk_b)]
    context = SearchController._build_context(results)
    assert "b" not in context


def test_build_context_custom_max_length_respected():
    """Verifica que _build_context respeita um max_length customizado passado como argumento."""
    results = [_make_result("hello"), _make_result("world")]
    context = SearchController._build_context(results, max_length=6)
    assert "world" not in context


def test_build_context_separator_not_appended_to_last_included_chunk():
    """Verifica que o separador nao e adicionado apos o ultimo chunk incluido no contexto."""
    results = [_make_result("First"), _make_result("Second")]
    context = SearchController._build_context(results)
    assert not context.endswith(CONTEXT_SEPARATOR)


# ---------------------------------------------------------------------------
# SearchController.ask
# ---------------------------------------------------------------------------


def test_ask_returns_no_info_response_when_no_results():
    """Verifica que ask retorna NO_INFO_RESPONSE e nao chama o LLM quando o vector store nao encontra resultados."""
    controller = _make_controller()
    controller.vector_store.search_similar.return_value = []
    answer = controller.ask("What is love?")
    assert answer == NO_INFO_RESPONSE
    controller.llm.ask.assert_not_called()


def test_ask_calls_vector_store_with_question_and_k():
    """Verifica que ask chama search_similar com a pergunta e o valor de k fornecidos."""
    controller = _make_controller()
    controller.vector_store.search_similar.return_value = []
    controller.ask("My question here", k=15)
    controller.vector_store.search_similar.assert_called_once_with(
        "My question here", k=15
    )


def test_ask_default_k_is_20():
    """Verifica que ask usa k=20 como valor padrao ao chamar search_similar."""
    controller = _make_controller()
    controller.vector_store.search_similar.return_value = []
    controller.ask("Some question?")
    controller.vector_store.search_similar.assert_called_once_with(
        "Some question?", k=20
    )


def test_ask_returns_llm_answer_when_results_found():
    """Verifica que ask retorna a resposta do LLM quando o vector store encontra resultados relevantes."""
    controller = _make_controller()
    results = [_make_result("Relevant content about the topic")]
    controller.vector_store.search_similar.return_value = results
    controller.llm.ask.return_value = "The answer from LLM"
    answer = controller.ask("Tell me about the topic")
    assert answer == "The answer from LLM"


def test_ask_passes_context_and_question_to_llm():
    """Verifica que ask passa o contexto recuperado e a pergunta original para o metodo ask do LLM."""
    controller = _make_controller()
    results = [_make_result("Context content")]
    controller.vector_store.search_similar.return_value = results
    controller.llm.ask.return_value = "LLM response"
    controller.ask("User question")
    call_args = controller.llm.ask.call_args
    context_arg, question_arg = call_args[0]
    assert "Context content" in context_arg
    assert question_arg == "User question"


def test_ask_llm_not_called_when_no_results():
    """Verifica que o LLM nao e chamado quando o vector store nao retorna nenhum resultado."""
    controller = _make_controller()
    controller.vector_store.search_similar.return_value = []
    controller.ask("Any question")
    controller.llm.ask.assert_not_called()


# ---------------------------------------------------------------------------
# Constantes do modulo
# ---------------------------------------------------------------------------


def test_constants_no_info_response_is_non_empty_string():
    """Verifica que NO_INFO_RESPONSE e uma string nao vazia."""
    assert isinstance(NO_INFO_RESPONSE, str)
    assert len(NO_INFO_RESPONSE) > 0


def test_constants_context_separator_is_string():
    """Verifica que CONTEXT_SEPARATOR e uma string."""
    assert isinstance(CONTEXT_SEPARATOR, str)


def test_constants_max_context_length_is_positive_int():
    """Verifica que MAX_CONTEXT_LENGTH e um inteiro positivo."""
    assert isinstance(MAX_CONTEXT_LENGTH, int)
    assert MAX_CONTEXT_LENGTH > 0
