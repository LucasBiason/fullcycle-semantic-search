"""Custom exceptions for the Semantic Search API."""


class ProviderNotConfiguredError(Exception):
    """Raised when no LLM/Embedding provider API key is set."""

    def __init__(
        self,
        message: str = "No LLM provider configured. Set GOOGLE_API_KEY or OPENAI_API_KEY.",
    ):
        super().__init__(message)


class IngestionError(Exception):
    """Raised when the PDF ingestion pipeline fails."""


class SearchError(Exception):
    """Raised when the semantic search pipeline fails."""


class VectorStoreError(Exception):
    """Raised when a vector store operation fails."""
