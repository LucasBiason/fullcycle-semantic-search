"""Ingestion controller. Orchestrates the PDF ingestion pipeline."""

import logging
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.services.embedding_service import embedding_service
from app.services.vector_store_service import vector_store_service

logger = logging.getLogger("semantic_search")

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


class IngestionController:
    """Orchestrates the PDF ingestion pipeline: load -> split -> clean -> store."""

    def __init__(self):
        self.embedding = embedding_service
        self.vector_store = vector_store_service

    def ingest_pdf(self) -> int:
        """Run the full ingestion pipeline.

        Returns:
            Number of chunks stored, or 0 if no chunks were generated.
        """
        provider = self.embedding.get_provider_name()
        logger.info("[ingest] Starting ingestion with %s...", provider)
        logger.info("[ingest] PDF: %s", settings.pdf_path)

        docs = self._load_pdf(settings.pdf_path)
        chunks = self._split_documents(docs)
        chunks = self._clean_metadata(chunks)

        if not chunks:
            logger.warning("[ingest] No chunks generated. Check the PDF.")
            return 0

        count = self.vector_store.store_documents(chunks)
        logger.info("[ingest] Ingestion completed. %d chunks stored.", count)
        return count

    @staticmethod
    def _load_pdf(pdf_path: str) -> list[Document]:
        """Load a PDF file and return one Document per page."""
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {path.absolute()}")
        docs = PyPDFLoader(str(path)).load()
        logger.info("[ingest] PDF loaded: %d pages", len(docs))
        return docs

    @staticmethod
    def _split_documents(docs: list[Document]) -> list[Document]:
        """Split documents into chunks using RecursiveCharacterTextSplitter."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        chunks = splitter.split_documents(docs)
        logger.info("[ingest] Chunks created: %d", len(chunks))
        return chunks

    @staticmethod
    def _clean_metadata(docs: list[Document]) -> list[Document]:
        """Remove metadata keys with empty string or None values."""
        return [
            Document(
                page_content=doc.page_content,
                metadata={k: v for k, v in doc.metadata.items() if v not in ("", None)},
            )
            for doc in docs
        ]


if __name__ == "__main__":
    IngestionController().ingest_pdf()
