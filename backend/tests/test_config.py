"""Tests for app.config - Settings class defaults and properties."""

from unittest.mock import patch

from app.config import Settings


def _make_settings(**overrides):
    """Construct a Settings instance ignoring real environment variables."""
    with patch.dict("os.environ", {}, clear=True):
        return Settings(**overrides)


# --- Defaults ---


def test_google_api_key_default():
    """Verifica que google_api_key tem valor padrao vazio quando nenhuma variavel de ambiente esta definida."""
    settings = _make_settings()
    assert settings.google_api_key == ""


def test_google_embedding_model_default():
    """Verifica que google_embedding_model tem o modelo padrao do Gemini quando nenhuma variavel de ambiente esta definida."""
    settings = _make_settings()
    assert settings.google_embedding_model == "models/gemini-embedding-001"


def test_google_llm_model_default():
    """Verifica que google_llm_model tem o modelo padrao do Gemini quando nenhuma variavel de ambiente esta definida."""
    settings = _make_settings()
    assert settings.google_llm_model == "gemini-2.5-flash-lite"


def test_openai_api_key_default():
    """Verifica que openai_api_key tem valor padrao vazio quando nenhuma variavel de ambiente esta definida."""
    settings = _make_settings()
    assert settings.openai_api_key == ""


def test_openai_embedding_model_default():
    """Verifica que openai_embedding_model tem o modelo padrao da OpenAI quando nenhuma variavel de ambiente esta definida."""
    settings = _make_settings()
    assert settings.openai_embedding_model == "text-embedding-3-small"


def test_openai_llm_model_default():
    """Verifica que openai_llm_model tem o modelo padrao da OpenAI quando nenhuma variavel de ambiente esta definida."""
    settings = _make_settings()
    assert settings.openai_llm_model == "gpt-5-nano"


def test_database_url_default():
    """Verifica que database_url tem a URL padrao de conexao PostgreSQL quando nenhuma variavel de ambiente esta definida."""
    settings = _make_settings()
    assert (
        settings.database_url
        == "postgresql+psycopg://postgres:postgres@localhost:5432/rag"
    )


def test_pg_vector_collection_name_default():
    """Verifica que pg_vector_collection_name tem o nome padrao da colecao quando nenhuma variavel de ambiente esta definida."""
    settings = _make_settings()
    assert settings.pg_vector_collection_name == "document_embeddings"


def test_pdf_path_default():
    """Verifica que pdf_path tem o caminho padrao do documento PDF quando nenhuma variavel de ambiente esta definida."""
    settings = _make_settings()
    assert settings.pdf_path == "assets/document.pdf"


# --- use_gemini property ---


def test_use_gemini_true_when_google_api_key_set():
    """Verifica que use_gemini retorna True quando GOOGLE_API_KEY esta configurada e OPENAI_API_KEY esta vazia."""
    settings = Settings(google_api_key="my-google-key", openai_api_key="")
    assert settings.use_gemini is True


def test_use_gemini_false_when_google_api_key_empty():
    """Verifica que use_gemini retorna False quando GOOGLE_API_KEY esta vazia."""
    settings = Settings(google_api_key="", openai_api_key="")
    assert settings.use_gemini is False


def test_use_gemini_true_when_both_keys_set():
    """Verifica que use_gemini retorna True quando ambas as chaves estao configuradas, indicando que Gemini tem prioridade."""
    settings = Settings(google_api_key="google-key", openai_api_key="openai-key")
    assert settings.use_gemini is True


def test_use_gemini_false_when_only_openai_key_set():
    """Verifica que use_gemini retorna False quando apenas OPENAI_API_KEY esta configurada."""
    settings = Settings(google_api_key="", openai_api_key="openai-key")
    assert settings.use_gemini is False


# --- use_openai property ---


def test_use_openai_true_when_only_openai_key_set():
    """Verifica que use_openai retorna True quando apenas OPENAI_API_KEY esta configurada."""
    settings = Settings(google_api_key="", openai_api_key="my-openai-key")
    assert settings.use_openai is True


def test_use_openai_false_when_neither_key_set():
    """Verifica que use_openai retorna False quando nenhuma chave de provedor esta configurada."""
    settings = Settings(google_api_key="", openai_api_key="")
    assert settings.use_openai is False


def test_use_openai_false_when_both_keys_set_gemini_takes_priority():
    """Verifica que use_openai retorna False quando ambas as chaves estao configuradas, pois Gemini tem prioridade."""
    settings = Settings(google_api_key="google-key", openai_api_key="openai-key")
    assert settings.use_openai is False


def test_use_openai_false_when_only_google_key_set():
    """Verifica que use_openai retorna False quando apenas GOOGLE_API_KEY esta configurada."""
    settings = Settings(google_api_key="google-key", openai_api_key="")
    assert settings.use_openai is False


# --- Mutual exclusivity ---


def test_gemini_and_openai_never_both_true():
    """Verifica que use_gemini e use_openai nunca sao ambos True simultaneamente, garantindo exclusao mutua."""
    settings = Settings(google_api_key="g-key", openai_api_key="o-key")
    assert not (settings.use_gemini and settings.use_openai)


def test_both_false_when_no_keys():
    """Verifica que use_gemini e use_openai sao ambos False quando nenhuma chave de provedor esta configurada."""
    settings = Settings(google_api_key="", openai_api_key="")
    assert settings.use_gemini is False
    assert settings.use_openai is False
