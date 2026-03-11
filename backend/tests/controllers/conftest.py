"""conftest for controllers tests.

Stubs out heavy third-party dependencies (numpy, langchain_community,
langchain_postgres) in sys.modules before any controller module is imported.
This prevents the numpy C-extension double-load crash that occurs when
pytest-cov instruments modules and the controllers/__init__.py eagerly
imports IngestionController, which pulls in PyPDFLoader and the full
langchain/pgvector stack.
"""

import sys
from unittest.mock import MagicMock


def _stub(name: str) -> MagicMock:
    """Insert a MagicMock as a sys.modules entry and return it."""
    mock = MagicMock()
    sys.modules[name] = mock
    return mock


if "langchain_postgres" not in sys.modules:
    _stub("numpy")
    _stub("numpy.core")
    _stub("langchain_postgres")
    _stub("langchain_postgres.v2")
    _stub("langchain_postgres.v2.vectorstores")
    _stub("langchain_community")
    _stub("langchain_community.document_loaders")
    _stub("langchain_community.document_loaders.pdf")
    _stub("langchain_community.vectorstores")
    _stub("langchain_community.vectorstores.pgvector")
