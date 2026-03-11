"""Vector store service. Encapsulates all pgVector operations."""

import logging

from langchain_core.documents import Document
from langchain_postgres import PGVector

from app.config import settings
from app.services.embedding_service import embedding_service
from app.exceptions import VectorStoreError

logger = logging.getLogger("semantic_search")


class VectorStoreService:
    """Encapsulates pgVector store initialization, document storage and search."""

    def __init__(self):
        self._store = None

    def _get_store(self) -> PGVector:
        """Initialize and return the PGVector store instance."""
        if self._store is not None:
            return self._store

        try:
            embeddings = embedding_service.get_embeddings()
            self._store = PGVector(
                embeddings=embeddings,
                collection_name=settings.pg_vector_collection_name,
                connection=settings.database_url,
                use_jsonb=True,
            )
            logger.info(
                "[vector_store] Initialized (collection: %s)",
                settings.pg_vector_collection_name,
            )
            return self._store
        except Exception as exc:
            raise VectorStoreError(f"Failed to initialize vector store: {exc}") from exc

    def clear_collection(self) -> None:
        """Delete all documents from the current collection."""
        try:
            store = self._get_store()
            store.delete_collection()
            self._store = None
            logger.info("[vector_store] Collection cleared")
        except Exception as exc:
            raise VectorStoreError(f"Failed to clear collection: {exc}") from exc

    def store_documents(self, chunks: list[Document], replace: bool = True) -> int:
        """Store document chunks in pgVector. Returns the number of stored chunks.

        When replace=True (default), clears existing documents before storing.
        """
        try:
            if replace:
                self.clear_collection()
            store = self._get_store()
            ids = [f"doc-{i}" for i in range(len(chunks))]
            store.add_documents(documents=chunks, ids=ids)
            logger.info("[vector_store] Stored %d documents", len(chunks))
            return len(chunks)
        except VectorStoreError:
            raise
        except Exception as exc:
            raise VectorStoreError(f"Failed to store documents: {exc}") from exc

    def search_similar(self, question: str, k: int = 10) -> list[tuple]:
        """Run similarity search. Returns list of (Document, score) tuples."""
        try:
            store = self._get_store()
            return store.similarity_search_with_score(question, k=k)
        except VectorStoreError:
            raise
        except Exception as exc:
            raise VectorStoreError(f"Similarity search failed: {exc}") from exc


vector_store_service = VectorStoreService()
