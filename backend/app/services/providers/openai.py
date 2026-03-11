"""OpenAI provider. Encapsulates all OpenAI embedding and LLM logic."""

import logging

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.config import settings
from app.services.providers.base import Provider

logger = logging.getLogger("semantic_search")


class OpenAIProvider(Provider):
    """OpenAI provider for embeddings and LLM."""

    def __init__(self):
        self._embeddings = None
        self._llm = None

    def get_embeddings(self):
        """Return OpenAIEmbeddings instance."""
        if self._embeddings is None:
            self._embeddings = OpenAIEmbeddings(model=settings.openai_embedding_model)
            logger.info(
                "[embedding] Initialized OpenAI (%s)", settings.openai_embedding_model
            )
        return self._embeddings

    def get_llm(self):
        """Return ChatOpenAI instance."""
        if self._llm is None:
            self._llm = ChatOpenAI(model=settings.openai_llm_model, temperature=0)
            logger.info("[llm] Initialized OpenAI (%s)", settings.openai_llm_model)
        return self._llm

    def get_provider_name(self) -> str:
        """Return provider name."""
        return "OpenAI"
