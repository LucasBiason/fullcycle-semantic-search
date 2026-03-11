"""CLI tools for testing and debugging the Semantic Search backend.

This module provides two interactive terminal interfaces that allow
manual validation of the search pipeline without using the frontend:

- cli.py  (direct)  : Calls the backend services directly via Python.
                       Does NOT require the API server to be running.
                       Useful for testing the pipeline in isolation.

- api_cli.py (HTTP) : Sends HTTP requests to the running FastAPI backend.
                       Requires `make serve` or `make up` first.
                       Useful for integration testing the full stack.

Quick start:
    make chat           # direct mode  (no server needed)
    make chat-api       # HTTP mode    (server must be running)

See each module's docstring for additional options.
"""
