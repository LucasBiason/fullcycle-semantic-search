"""Gemini provider. Encapsulates all Google Gemini embedding and LLM logic."""

import logging

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from app.config import settings
from app.services.providers.base import Provider

logger = logging.getLogger("semantic_search")


class GeminiProvider(Provider):
    """Google Gemini provider for embeddings and LLM."""

    def __init__(self):
        self._embeddings = None
        self._llm = None

    def get_embeddings(self):
        """Return GoogleGenerativeAIEmbeddings instance."""
        if self._embeddings is None:
            self._embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.google_embedding_model,
                google_api_key=settings.google_api_key,
            )
            logger.info(
                "[embedding] Initialized Gemini (%s)", settings.google_embedding_model
            )
        return self._embeddings

    def get_llm(self):
        """Return ChatGoogleGenerativeAI instance."""
        if self._llm is None:
            self._llm = ChatGoogleGenerativeAI(
                model=settings.google_llm_model,
                google_api_key=settings.google_api_key,
                temperature=0,
            )
            logger.info("[llm] Initialized Gemini (%s)", settings.google_llm_model)
        return self._llm

    def get_provider_name(self) -> str:
        """Return provider name."""
        return "Gemini"
