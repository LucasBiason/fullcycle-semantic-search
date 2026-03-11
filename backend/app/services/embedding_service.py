"""Embedding service factory. Creates the appropriate provider based on configuration."""

import logging

from app.services.providers import Provider, create_provider
from app.exceptions import ProviderNotConfiguredError

logger = logging.getLogger("semantic_search")


class EmbeddingService:
    """Factory that creates and holds the correct provider for embeddings.

    Consumers receive this service ready to use and call get_embeddings()
    or get_provider_name() without knowing which provider is behind it.
    """

    def __init__(self):
        self._provider: Provider | None = None

    def _get_provider(self) -> Provider:
        """Create and cache the provider based on configuration."""
        if self._provider is not None:
            return self._provider

        self._provider = create_provider()
        logger.info("[embedding] Provider: %s", self._provider.get_provider_name())
        return self._provider

    def get_embeddings(self):
        """Return the configured embedding model instance."""
        return self._get_provider().get_embeddings()

    def get_provider_name(self) -> str:
        """Return human-readable name of the active embedding provider."""
        try:
            return self._get_provider().get_provider_name()
        except ProviderNotConfiguredError:
            return "None"


embedding_service = EmbeddingService()
