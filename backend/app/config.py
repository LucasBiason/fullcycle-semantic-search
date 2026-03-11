"""Central configuration via pydantic-settings and env."""

from pathlib import Path

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parent.parent.parent / "configs" / "backend.env"
load_dotenv(_env_path)


class Settings(BaseSettings):
    google_api_key: str = ""
    google_embedding_model: str = "models/gemini-embedding-001"
    google_llm_model: str = "gemini-2.5-flash-lite"

    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    openai_llm_model: str = "gpt-5-nano"

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/rag"
    pg_vector_collection_name: str = "document_embeddings"

    pdf_path: str = "assets/document.pdf"

    @property
    def use_gemini(self) -> bool:
        return bool(self.google_api_key)

    @property
    def use_openai(self) -> bool:
        return bool(self.openai_api_key) and not self.use_gemini


settings = Settings()
