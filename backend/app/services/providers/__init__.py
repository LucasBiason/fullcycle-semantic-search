"""AI provider implementations."""

from app.config import settings
from app.services.providers.base import Provider
from app.services.providers.gemini import GeminiProvider
from app.services.providers.openai import OpenAIProvider
from app.exceptions import ProviderNotConfiguredError

__all__ = [
    "GeminiProvider",
    "OpenAIProvider",
    "Provider",
    "create_provider",
    "create_fallback_provider",
]


def create_provider() -> Provider:
    """Create the primary provider based on configuration."""
    if settings.use_gemini:
        return GeminiProvider()
    if settings.use_openai:
        return OpenAIProvider()
    raise ProviderNotConfiguredError()


def create_fallback_provider() -> Provider | None:
    """Create the fallback provider if both APIs are configured."""
    if settings.use_gemini and settings.openai_api_key:
        return OpenAIProvider()
    if settings.use_openai and settings.google_api_key:
        return GeminiProvider()
    return None
