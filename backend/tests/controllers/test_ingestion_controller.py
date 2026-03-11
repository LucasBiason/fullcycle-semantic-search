"""Tests for app.controllers.ingestion_controller - IngestionController."""

import pytest
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document

from app.controllers.ingestion_controller import IngestionController


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_controller():
    """Cria um IngestionController com servicos mockados, sem chamar __init__."""
    controller = IngestionController.__new__(IngestionController)
    controller.embedding = MagicMock()
    controller.vector_store = MagicMock()
    return controller


def _make_docs(n=3):
    """Cria uma lista de n Documents de teste com conteudo e metadados simples."""
    return [
        Document(page_content=f"Chunk {i}", metadata={"page": i}) for i in range(n)
    ]


# ---------------------------------------------------------------------------
# IngestionController.__init__
# ---------------------------------------------------------------------------


@patch("app.controllers.ingestion_controller.vector_store_service")
@patch("app.controllers.ingestion_controller.embedding_service")
def test_init_assigns_embedding_service(mock_embedding, mock_vector_store):
    """Verifica que __init__ atribui o embedding_service ao atributo embedding do controller."""
    controller = IngestionController()
    assert controller.embedding is mock_embedding


@patch("app.controllers.ingestion_controller.vector_store_service")
@patch("app.controllers.ingestion_controller.embedding_service")
def test_init_assigns_vector_store_service(mock_embedding, mock_vector_store):
    """Verifica que __init__ atribui o vector_store_service ao atributo vector_store do controller."""
    controller = IngestionController()
    assert controller.vector_store is mock_vector_store


# ---------------------------------------------------------------------------
# IngestionController._load_pdf
# ---------------------------------------------------------------------------


def test_load_pdf_raises_file_not_found_for_missing_file():
    """Verifica que _load_pdf levanta FileNotFoundError com mensagem 'PDF not found' para arquivo inexistente."""
    with pytest.raises(FileNotFoundError, match="PDF not found"):
        IngestionController._load_pdf("nonexistent/path/file.pdf")


def test_load_pdf_raises_file_not_found_message_contains_path():
    """Verifica que a mensagem de FileNotFoundError contem o caminho do arquivo informado."""
    with pytest.raises(FileNotFoundError) as exc_info:
        IngestionController._load_pdf("missing.pdf")
    assert "missing.pdf" in str(exc_info.value)


@patch("app.controllers.ingestion_controller.PyPDFLoader")
def test_load_pdf_loads_pdf_when_file_exists(mock_loader_class, tmp_path):
    """Verifica que _load_pdf usa PyPDFLoader para carregar um arquivo PDF existente e retorna seus documentos."""
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 fake content")

    mock_doc = Document(page_content="Page content", metadata={"page": 0})
    mock_loader = MagicMock()
    mock_loader.load.return_value = [mock_doc]
    mock_loader_class.return_value = mock_loader

    result = IngestionController._load_pdf(str(pdf_file))

    mock_loader_class.assert_called_once_with(str(pdf_file))
    mock_loader.load.assert_called_once()
    assert result == [mock_doc]


@patch("app.controllers.ingestion_controller.PyPDFLoader")
def test_load_pdf_returns_list_of_documents(mock_loader_class, tmp_path):
    """Verifica que _load_pdf retorna uma lista com todos os documentos carregados pelo loader."""
    pdf_file = tmp_path / "multi.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 fake")

    docs = [
        Document(page_content=f"Page {i}", metadata={"page": i}) for i in range(3)
    ]
    mock_loader = MagicMock()
    mock_loader.load.return_value = docs
    mock_loader_class.return_value = mock_loader

    result = IngestionController._load_pdf(str(pdf_file))
    assert len(result) == 3


# ---------------------------------------------------------------------------
# IngestionController._split_documents
# ---------------------------------------------------------------------------


def test_split_documents_empty_list_returns_empty_list():
    """Verifica que _split_documents retorna lista vazia quando recebe lista vazia."""
    result = IngestionController._split_documents([])
    assert result == []


def test_split_documents_short_doc_below_chunk_size_returns_single_chunk():
    """Verifica que um documento curto (abaixo do tamanho de chunk) resulta em pelo menos um chunk com o conteudo original."""
    doc = Document(page_content="Short content.", metadata={"page": 0})
    result = IngestionController._split_documents([doc])
    assert len(result) >= 1
    combined = " ".join(chunk.page_content for chunk in result)
    assert "Short content." in combined


def test_split_documents_long_doc_produces_multiple_chunks():
    """Verifica que um documento longo e dividido em mais de um chunk."""
    long_text = "word " * 500
    doc = Document(page_content=long_text, metadata={"page": 0})
    result = IngestionController._split_documents([doc])
    assert len(result) > 1


def test_split_documents_all_chunks_are_documents():
    """Verifica que todos os itens retornados por _split_documents sao instancias de Document."""
    doc = Document(page_content="Some reasonable text to split. " * 50, metadata={})
    result = IngestionController._split_documents([doc])
    for chunk in result:
        assert isinstance(chunk, Document)


def test_split_documents_multiple_docs_are_all_processed():
    """Verifica que todos os documentos da lista de entrada sao processados e geram chunks."""
    docs = [
        Document(page_content=f"Content for page {i}. " * 10, metadata={"page": i})
        for i in range(3)
    ]
    result = IngestionController._split_documents(docs)
    assert len(result) >= 3


# ---------------------------------------------------------------------------
# IngestionController._clean_metadata
# ---------------------------------------------------------------------------


def test_clean_metadata_removes_none_values():
    """Verifica que _clean_metadata remove campos com valor None dos metadados."""
    doc = Document(page_content="Text", metadata={"page": 1, "author": None})
    result = IngestionController._clean_metadata([doc])
    assert "author" not in result[0].metadata
    assert result[0].metadata["page"] == 1


def test_clean_metadata_removes_empty_string_values():
    """Verifica que _clean_metadata remove campos com string vazia dos metadados."""
    doc = Document(page_content="Text", metadata={"page": 2, "title": ""})
    result = IngestionController._clean_metadata([doc])
    assert "title" not in result[0].metadata
    assert result[0].metadata["page"] == 2


def test_clean_metadata_keeps_zero_value():
    """Verifica que _clean_metadata mantem campos com valor zero (0) nos metadados."""
    doc = Document(page_content="Text", metadata={"page": 0, "score": 0})
    result = IngestionController._clean_metadata([doc])
    assert result[0].metadata["page"] == 0
    assert result[0].metadata["score"] == 0


def test_clean_metadata_keeps_false_value():
    """Verifica que _clean_metadata mantem campos com valor False nos metadados."""
    doc = Document(page_content="Text", metadata={"indexed": False})
    result = IngestionController._clean_metadata([doc])
    assert result[0].metadata["indexed"] is False


def test_clean_metadata_empty_list_returns_empty_list():
    """Verifica que _clean_metadata retorna lista vazia quando recebe lista vazia."""
    result = IngestionController._clean_metadata([])
    assert result == []


def test_clean_metadata_preserves_page_content():
    """Verifica que _clean_metadata nao altera o page_content dos documentos."""
    doc = Document(page_content="Important text here", metadata={"key": None})
    result = IngestionController._clean_metadata([doc])
    assert result[0].page_content == "Important text here"


def test_clean_metadata_multiple_docs_all_cleaned():
    """Verifica que _clean_metadata limpa os metadados de todos os documentos da lista."""
    docs = [
        Document(page_content="Doc 1", metadata={"page": 1, "empty": ""}),
        Document(page_content="Doc 2", metadata={"page": 2, "nothing": None}),
    ]
    result = IngestionController._clean_metadata(docs)
    assert len(result) == 2
    assert "empty" not in result[0].metadata
    assert "nothing" not in result[1].metadata
    assert result[0].metadata["page"] == 1
    assert result[1].metadata["page"] == 2


def test_clean_metadata_returns_new_document_instances():
    """Verifica que _clean_metadata retorna novas instancias de Document, nao os objetos originais."""
    doc = Document(page_content="Text", metadata={"page": 1})
    result = IngestionController._clean_metadata([doc])
    assert result[0] is not doc


def test_clean_metadata_without_removals_stays_intact():
    """Verifica que _clean_metadata nao altera metadados que nao possuem valores invalidos."""
    doc = Document(page_content="Text", metadata={"page": 5, "source": "doc.pdf"})
    result = IngestionController._clean_metadata([doc])
    assert result[0].metadata == {"page": 5, "source": "doc.pdf"}


# ---------------------------------------------------------------------------
# IngestionController.ingest_pdf
# ---------------------------------------------------------------------------


@patch("app.controllers.ingestion_controller.IngestionController._load_pdf")
@patch("app.controllers.ingestion_controller.IngestionController._split_documents")
@patch("app.controllers.ingestion_controller.IngestionController._clean_metadata")
def test_ingest_pdf_returns_count_from_vector_store(mock_clean, mock_split, mock_load):
    """Verifica que ingest_pdf retorna o numero de chunks armazenados pelo vector store."""
    controller = _make_controller()
    controller.embedding.get_provider_name.return_value = "gemini"

    chunks = _make_docs(5)
    mock_load.return_value = _make_docs(2)
    mock_split.return_value = chunks
    mock_clean.return_value = chunks
    controller.vector_store.store_documents.return_value = 5

    result = controller.ingest_pdf()

    assert result == 5
    controller.vector_store.store_documents.assert_called_once_with(chunks)


@patch("app.controllers.ingestion_controller.IngestionController._load_pdf")
@patch("app.controllers.ingestion_controller.IngestionController._split_documents")
@patch("app.controllers.ingestion_controller.IngestionController._clean_metadata")
def test_ingest_pdf_returns_zero_when_no_chunks_generated(
    mock_clean, mock_split, mock_load
):
    """Verifica que ingest_pdf retorna 0 e nao chama store_documents quando nenhum chunk e gerado."""
    controller = _make_controller()
    controller.embedding.get_provider_name.return_value = "openai"

    mock_load.return_value = _make_docs(1)
    mock_split.return_value = []
    mock_clean.return_value = []

    result = controller.ingest_pdf()

    assert result == 0
    controller.vector_store.store_documents.assert_not_called()


@patch("app.controllers.ingestion_controller.IngestionController._load_pdf")
@patch("app.controllers.ingestion_controller.IngestionController._split_documents")
@patch("app.controllers.ingestion_controller.IngestionController._clean_metadata")
def test_ingest_pdf_pipeline_order_load_split_clean_store(
    mock_clean, mock_split, mock_load
):
    """Verifica que ingest_pdf executa as etapas do pipeline na ordem correta: load, split, clean, store."""
    controller = _make_controller()
    controller.embedding.get_provider_name.return_value = "gemini"

    call_order = []
    raw_docs = _make_docs(2)
    split_docs = _make_docs(4)
    clean_docs = _make_docs(4)

    mock_load.side_effect = lambda _: call_order.append("load") or raw_docs
    mock_split.side_effect = lambda d: call_order.append("split") or split_docs
    mock_clean.side_effect = lambda d: call_order.append("clean") or clean_docs
    controller.vector_store.store_documents.side_effect = (
        lambda d: call_order.append("store") or 4
    )

    controller.ingest_pdf()

    assert call_order == ["load", "split", "clean", "store"]


@patch("app.controllers.ingestion_controller.IngestionController._load_pdf")
@patch("app.controllers.ingestion_controller.IngestionController._split_documents")
@patch("app.controllers.ingestion_controller.IngestionController._clean_metadata")
def test_ingest_pdf_uses_pdf_path_from_settings(mock_clean, mock_split, mock_load):
    """Verifica que ingest_pdf passa o caminho do PDF configurado em settings para _load_pdf."""
    controller = _make_controller()
    controller.embedding.get_provider_name.return_value = "gemini"

    chunks = _make_docs(2)
    mock_load.return_value = chunks
    mock_split.return_value = chunks
    mock_clean.return_value = chunks
    controller.vector_store.store_documents.return_value = 2

    with patch("app.controllers.ingestion_controller.settings") as mock_settings:
        mock_settings.pdf_path = "custom/path.pdf"
        controller.ingest_pdf()

    mock_load.assert_called_once_with("custom/path.pdf")


@patch("app.controllers.ingestion_controller.IngestionController._load_pdf")
@patch("app.controllers.ingestion_controller.IngestionController._split_documents")
@patch("app.controllers.ingestion_controller.IngestionController._clean_metadata")
def test_ingest_pdf_calls_get_provider_name_for_logging(
    mock_clean, mock_split, mock_load
):
    """Verifica que ingest_pdf chama get_provider_name no servico de embedding (usado para logging)."""
    controller = _make_controller()
    controller.embedding.get_provider_name.return_value = "gemini"

    chunks = _make_docs(1)
    mock_load.return_value = chunks
    mock_split.return_value = chunks
    mock_clean.return_value = chunks
    controller.vector_store.store_documents.return_value = 1

    controller.ingest_pdf()

    controller.embedding.get_provider_name.assert_called_once()
