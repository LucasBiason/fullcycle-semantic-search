"""Abstract base class for AI providers."""

from abc import ABC, abstractmethod


class Provider(ABC):
    """Abstract provider that encapsulates both embedding and LLM for a given API."""

    @abstractmethod
    def get_embeddings(self):
        """Return the embedding model instance."""

    @abstractmethod
    def get_llm(self):
        """Return the LLM model instance."""

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return human-readable provider name."""
