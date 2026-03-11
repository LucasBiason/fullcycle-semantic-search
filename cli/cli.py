"""Direct CLI chat - tests the search pipeline without the API server.

Calls SearchController and EmbeddingService directly, bypassing FastAPI
entirely. This is useful for validating that ingestion, embeddings, vector
search, and LLM answer generation work correctly in isolation.

Requirements:
    - PostgreSQL with pgVector running (make db-up)
    - PDF already ingested (make ingest)
    - Valid API keys in .env (GOOGLE_API_KEY or OPENAI_API_KEY)

Usage:
    make chat
    PYTHONPATH=backend python -m cli.cli

Example session:
    ============================================================
      Semantic Search - Direct CLI
      Provider: Gemini
    ============================================================
      Type your question and press Enter.
      Type 'exit', 'quit' or 'q' to end the session.
    ============================================================

    QUESTION: Quais empresas estao listadas?
    ANSWER: O documento lista empresas como Helix, Lunar, Orbital...

    QUESTION: exit
    Session ended.
"""

import sys
from pathlib import Path

_backend = str(Path(__file__).resolve().parent.parent / "backend")
if _backend not in sys.path:
    sys.path.insert(0, _backend)

from app.controllers.search_controller import SearchController  # noqa: E402
from app.services.embedding_service import embedding_service  # noqa: E402


def main() -> None:
    """Run interactive direct CLI chat loop."""
    provider = embedding_service.get_provider_name()
    print("=" * 60)
    print("  Semantic Search - Direct CLI")
    print(f"  Provider: {provider}")
    print("=" * 60)
    print("  Type your question and press Enter.")
    print("  Type 'exit', 'quit' or 'q' to end the session.")
    print("=" * 60)
    print()

    controller = SearchController()

    while True:
        try:
            question = input("QUESTION: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSession ended.")
            break

        if not question:
            continue

        if question.lower() in ("exit", "quit", "q"):
            print("Session ended.")
            break

        answer = controller.ask(question, k=20)
        print(f"ANSWER: {answer}\n")


if __name__ == "__main__":
    main()
