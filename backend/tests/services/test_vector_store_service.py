"""Tests for app.services.vector_store_service.VectorStoreService."""

from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document

from app.exceptions import VectorStoreError
from app.services.vector_store_service import VectorStoreService


# ---------------------------------------------------------------------------
# _get_store
# ---------------------------------------------------------------------------


@patch("app.services.vector_store_service.PGVector")
@patch("app.services.vector_store_service.embedding_service")
def test_vector_store_service_initializes_pgvector_on_first_call(
    mock_embedding_service, mock_pgvector_cls
):
    """Verifica que _get_store instancia PGVector exatamente uma vez na
    primeira chamada e retorna a instancia criada."""
    mock_embeddings = MagicMock()
    mock_embedding_service.get_embeddings.return_value = mock_embeddings
    mock_store = MagicMock()
    mock_pgvector_cls.return_value = mock_store

    service = VectorStoreService()
    result = service._get_store()

    mock_pgvector_cls.assert_called_once()
    assert result is mock_store


@patch("app.services.vector_store_service.PGVector")
@patch("app.services.vector_store_service.embedding_service")
def test_vector_store_service_caches_store_on_second_call(
    mock_embedding_service, mock_pgvector_cls
):
    """Verifica que _get_store reutiliza a instancia de PGVector criada na
    primeira chamada, sem instanciar PGVector novamente."""
    mock_embedding_service.get_embeddings.return_value = MagicMock()
    mock_store = MagicMock()
    mock_pgvector_cls.return_value = mock_store

    service = VectorStoreService()
    first = service._get_store()
    second = service._get_store()

    mock_pgvector_cls.assert_called_once()
    assert first is second


@patch("app.services.vector_store_service.PGVector")
@patch("app.services.vector_store_service.embedding_service")
def test_vector_store_service_passes_embeddings_to_pgvector(
    mock_embedding_service, mock_pgvector_cls
):
    """Verifica que _get_store passa o objeto de embeddings retornado pelo
    embedding_service como argumento 'embeddings' ao construtor de PGVector."""
    mock_embeddings = MagicMock()
    mock_embedding_service.get_embeddings.return_value = mock_embeddings
    mock_pgvector_cls.return_value = MagicMock()

    service = VectorStoreService()
    service._get_store()

    call_kwargs = mock_pgvector_cls.call_args.kwargs
    assert call_kwargs["embeddings"] is mock_embeddings


@patch("app.services.vector_store_service.PGVector")
@patch("app.services.vector_store_service.embedding_service")
def test_vector_store_service_passes_use_jsonb_true(
    mock_embedding_service, mock_pgvector_cls
):
    """Verifica que _get_store passa o argumento 'use_jsonb=True' ao
    construtor de PGVector."""
    mock_embedding_service.get_embeddings.return_value = MagicMock()
    mock_pgvector_cls.return_value = MagicMock()

    service = VectorStoreService()
    service._get_store()

    call_kwargs = mock_pgvector_cls.call_args.kwargs
    assert call_kwargs["use_jsonb"] is True


@patch("app.services.vector_store_service.embedding_service")
def test_vector_store_service_raises_vector_store_error_when_pgvector_init_fails(
    mock_embedding_service,
):
    """Verifica que _get_store lanca VectorStoreError com a mensagem
    'Failed to initialize vector store' quando a inicializacao falha."""
    mock_embedding_service.get_embeddings.side_effect = RuntimeError(
        "connection refused"
    )

    service = VectorStoreService()
    with pytest.raises(VectorStoreError) as exc_info:
        service._get_store()

    assert "Failed to initialize vector store" in str(exc_info.value)


@patch("app.services.vector_store_service.embedding_service")
def test_vector_store_service_error_wraps_original_exception(mock_embedding_service):
    """Verifica que o VectorStoreError lancado por _get_store encapsula a
    excecao original como causa (via __cause__)."""
    original_error = RuntimeError("db down")
    mock_embedding_service.get_embeddings.side_effect = original_error

    service = VectorStoreService()
    with pytest.raises(VectorStoreError) as exc_info:
        service._get_store()

    assert exc_info.value.__cause__ is original_error


@patch("app.services.vector_store_service.PGVector")
@patch("app.services.vector_store_service.embedding_service")
def test_vector_store_service_skips_reinit_when_store_already_cached(
    mock_embedding_service, mock_pgvector_cls
):
    """Verifica que _get_store nao instancia PGVector nem chama get_embeddings
    quando o store ja esta armazenado no atributo _store do servico."""
    prebuilt_store = MagicMock()
    service = VectorStoreService()
    service._store = prebuilt_store

    result = service._get_store()

    mock_pgvector_cls.assert_not_called()
    mock_embedding_service.get_embeddings.assert_not_called()
    assert result is prebuilt_store


# ---------------------------------------------------------------------------
# store_documents
# ---------------------------------------------------------------------------


@patch("app.services.vector_store_service.PGVector")
@patch("app.services.vector_store_service.embedding_service")
def test_vector_store_service_returns_count_of_stored_chunks(
    mock_embedding_service, mock_pgvector_cls
):
    """Verifica que store_documents retorna o numero correto de chunks
    armazenados, correspondente ao tamanho da lista de documentos enviada."""
    mock_embedding_service.get_embeddings.return_value = MagicMock()
    mock_store = MagicMock()
    mock_pgvector_cls.return_value = mock_store

    chunks = [
        Document(page_content="chunk 1"),
        Document(page_content="chunk 2"),
        Document(page_content="chunk 3"),
    ]

    service = VectorStoreService()
    result = service.store_documents(chunks)

    assert result == 3


@patch("app.services.vector_store_service.PGVector")
@patch("app.services.vector_store_service.embedding_service")
def test_vector_store_service_calls_add_documents_with_chunks_and_ids(
    mock_embedding_service, mock_pgvector_cls
):
    """Verifica que store_documents chama add_documents no store com os
    documentos e os IDs sequenciais no formato 'doc-N'."""
    mock_embedding_service.get_embeddings.return_value = MagicMock()
    mock_store = MagicMock()
    mock_pgvector_cls.return_value = mock_store

    chunks = [Document(page_content="a"), Document(page_content="b")]

    service = VectorStoreService()
    service.store_documents(chunks)

    mock_store.add_documents.assert_called_once_with(
        documents=chunks, ids=["doc-0", "doc-1"]
    )


@patch("app.services.vector_store_service.PGVector")
@patch("app.services.vector_store_service.embedding_service")
def test_vector_store_service_returns_zero_for_empty_list(
    mock_embedding_service, mock_pgvector_cls
):
    """Verifica que store_documents retorna 0 quando a lista de documentos
    enviada esta vazia."""
    mock_embedding_service.get_embeddings.return_value = MagicMock()
    mock_pgvector_cls.return_value = MagicMock()

    service = VectorStoreService()
    result = service.store_documents([])

    assert result == 0


@patch("app.services.vector_store_service.PGVector")
@patch("app.services.vector_store_service.embedding_service")
def test_vector_store_service_raises_vector_store_error_when_add_documents_fails(
    mock_embedding_service, mock_pgvector_cls
):
    """Verifica que store_documents lanca VectorStoreError com a mensagem
    'Failed to store documents' quando add_documents lanca uma excecao."""
    mock_embedding_service.get_embeddings.return_value = MagicMock()
    mock_store = MagicMock()
    mock_store.add_documents.side_effect = RuntimeError("insert failed")
    mock_pgvector_cls.return_value = mock_store

    service = VectorStoreService()
    with pytest.raises(VectorStoreError) as exc_info:
        service.store_documents([Document(page_content="x")])

    assert "Failed to store documents" in str(exc_info.value)


@patch("app.services.vector_store_service.embedding_service")
def test_vector_store_service_reraises_vector_store_error_from_get_store_on_store(
    mock_embedding_service,
):
    """Verifica que store_documents propaga VectorStoreError quando _get_store
    falha ao inicializar o armazenamento vetorial."""
    mock_embedding_service.get_embeddings.side_effect = RuntimeError("db error")

    service = VectorStoreService()
    with pytest.raises(VectorStoreError):
        service.store_documents([Document(page_content="x")])


@patch("app.services.vector_store_service.PGVector")
@patch("app.services.vector_store_service.embedding_service")
def test_vector_store_service_vector_store_error_from_get_store_is_reraised_unchanged(
    mock_embedding_service, mock_pgvector_cls
):
    """Verifica que store_documents repropaga o mesmo objeto VectorStoreError
    lancado por clear_collection, sem encapsular em outra excecao."""
    specific_error = VectorStoreError("init failed")

    service = VectorStoreService()
    with patch.object(service, "clear_collection", side_effect=specific_error):
        with pytest.raises(VectorStoreError) as exc_info:
            service.store_documents([Document(page_content="x")])

    assert exc_info.value is specific_error


# ---------------------------------------------------------------------------
# search_similar
# ---------------------------------------------------------------------------


@patch("app.services.vector_store_service.PGVector")
@patch("app.services.vector_store_service.embedding_service")
def test_vector_store_service_delegates_to_similarity_search_with_score(
    mock_embedding_service, mock_pgvector_cls
):
    """Verifica que search_similar delega a busca ao metodo
    similarity_search_with_score do store, passando a query e k=10 por
    padrao, e retorna os resultados obtidos."""
    mock_embedding_service.get_embeddings.return_value = MagicMock()
    mock_store = MagicMock()
    expected_results = [(Document(page_content="result"), 0.95)]
    mock_store.similarity_search_with_score.return_value = expected_results
    mock_pgvector_cls.return_value = mock_store

    service = VectorStoreService()
    result = service.search_similar("test question")

    mock_store.similarity_search_with_score.assert_called_once_with(
        "test question", k=10
    )
    assert result is expected_results


@patch("app.services.vector_store_service.PGVector")
@patch("app.services.vector_store_service.embedding_service")
def test_vector_store_service_passes_custom_k_to_similarity_search(
    mock_embedding_service, mock_pgvector_cls
):
    """Verifica que search_similar repassa o valor de k personalizado ao
    metodo similarity_search_with_score do store."""
    mock_embedding_service.get_embeddings.return_value = MagicMock()
    mock_store = MagicMock()
    mock_store.similarity_search_with_score.return_value = []
    mock_pgvector_cls.return_value = mock_store

    service = VectorStoreService()
    service.search_similar("question", k=5)

    mock_store.similarity_search_with_score.assert_called_once_with("question", k=5)


@patch("app.services.vector_store_service.PGVector")
@patch("app.services.vector_store_service.embedding_service")
def test_vector_store_service_raises_vector_store_error_when_search_fails(
    mock_embedding_service, mock_pgvector_cls
):
    """Verifica que search_similar lanca VectorStoreError com a mensagem
    'Similarity search failed' quando similarity_search_with_score falha."""
    mock_embedding_service.get_embeddings.return_value = MagicMock()
    mock_store = MagicMock()
    mock_store.similarity_search_with_score.side_effect = RuntimeError(
        "search failed"
    )
    mock_pgvector_cls.return_value = mock_store

    service = VectorStoreService()
    with pytest.raises(VectorStoreError) as exc_info:
        service.search_similar("question")

    assert "Similarity search failed" in str(exc_info.value)


@patch("app.services.vector_store_service.embedding_service")
def test_vector_store_service_reraises_vector_store_error_from_get_store_on_search(
    mock_embedding_service,
):
    """Verifica que search_similar propaga VectorStoreError quando _get_store
    falha ao inicializar o armazenamento vetorial."""
    mock_embedding_service.get_embeddings.side_effect = RuntimeError("init error")

    service = VectorStoreService()
    with pytest.raises(VectorStoreError):
        service.search_similar("question")


@patch("app.services.vector_store_service.PGVector")
@patch("app.services.vector_store_service.embedding_service")
def test_vector_store_service_vector_store_error_from_get_store_is_reraised_unchanged_in_search(
    mock_embedding_service, mock_pgvector_cls
):
    """Verifica que search_similar repropaga o mesmo objeto VectorStoreError
    lancado por _get_store, sem encapsular em outra excecao."""
    specific_error = VectorStoreError("init failed")

    service = VectorStoreService()
    with patch.object(service, "_get_store", side_effect=specific_error):
        with pytest.raises(VectorStoreError) as exc_info:
            service.search_similar("question")

    assert exc_info.value is specific_error


@patch("app.services.vector_store_service.PGVector")
@patch("app.services.vector_store_service.embedding_service")
def test_vector_store_service_returns_empty_list_when_no_matches(
    mock_embedding_service, mock_pgvector_cls
):
    """Verifica que search_similar retorna uma lista vazia quando
    similarity_search_with_score nao encontra nenhum resultado correspondente."""
    mock_embedding_service.get_embeddings.return_value = MagicMock()
    mock_store = MagicMock()
    mock_store.similarity_search_with_score.return_value = []
    mock_pgvector_cls.return_value = mock_store

    service = VectorStoreService()
    result = service.search_similar("no match query")

    assert result == []
