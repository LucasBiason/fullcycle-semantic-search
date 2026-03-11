"""HTTP CLI chat - tests the full stack via API requests.

Sends HTTP requests to the running FastAPI backend, exercising the same
code path that the React frontend uses. This is useful for integration
testing: it validates that the API server, routing, controllers, services,
database, and LLM are all wired together and responding correctly.

Requirements:
    - Backend running (make serve or make up)
    - PDF already ingested (make ingest or POST /api/ingest)

Usage:
    make chat-api
    python -m cli.api_cli
    python -m cli.api_cli --url http://localhost:8000 --k 10

Options:
    --url   Backend base URL  (default: http://localhost:8000)
    --k     Number of chunks to retrieve  (default: 20)

Example session:
    ============================================================
      Semantic Search - HTTP CLI
      Backend: http://localhost:8000
      Provider: Gemini
    ============================================================
      Type your question and press Enter.
      Type 'exit', 'quit' or 'q' to end the session.
    ============================================================

    QUESTION: Quais setores aparecem no documento?
    ANSWER: O documento apresenta empresas dos setores de Industria...

    QUESTION: exit
    Session ended.
"""

import argparse
import sys

import requests

DEFAULT_URL = "http://localhost:8000"


def main() -> None:
    """Run interactive HTTP CLI chat loop."""
    parser = argparse.ArgumentParser(
        description="Test the Semantic Search API interactively via terminal"
    )
    parser.add_argument("--url", default=DEFAULT_URL, help="Backend base URL")
    parser.add_argument(
        "--k", type=int, default=20, help="Number of chunks to retrieve"
    )
    args = parser.parse_args()

    base_url = args.url.rstrip("/")

    try:
        health = requests.get(f"{base_url}/health", timeout=5)
        health.raise_for_status()
        info = health.json()
    except requests.ConnectionError:
        print(f"ERROR: Backend not reachable at {base_url}")
        print("Start the backend first: make serve  or  make up")
        sys.exit(1)
    except requests.RequestException as exc:
        print(f"ERROR: Health check failed: {exc}")
        sys.exit(1)

    print("=" * 60)
    print("  Semantic Search - HTTP CLI")
    print(f"  Backend: {base_url}")
    print(f"  Provider: {info.get('provider', 'unknown')}")
    print("=" * 60)
    print("  Type your question and press Enter.")
    print("  Type 'exit', 'quit' or 'q' to end the session.")
    print("=" * 60)
    print()

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

        try:
            response = requests.post(
                f"{base_url}/api/search",
                json={"question": question, "k": args.k},
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            print(f"ANSWER: {data['answer']}\n")
        except requests.RequestException as exc:
            print(f"ERROR: {exc}\n")


if __name__ == "__main__":
    main()
