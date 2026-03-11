# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-11

### Added

- PDF ingestion pipeline with automatic chunking and metadata cleaning
- Semantic search over ingested documents using pgVector similarity search
- LLM-powered answer generation from retrieved context (RAG pattern)
- Multi-provider support for embeddings and LLM (Google Gemini and OpenAI)
- Automatic fallback between LLM providers when both are configured
- Guardrail system that refuses to answer questions outside document scope
- FastAPI backend with health, ingestion, and search endpoints
- React 19 + TypeScript + Tailwind CSS v4 frontend with dark SaaS theme
- Multi-conversation support with localStorage persistence
- Interactive CLI tools for testing the backend directly (`make chat`) and via HTTP (`make chat-api`)
- Docker Compose setup with PostgreSQL + pgVector, backend, and frontend
- Nginx reverse proxy in frontend container for API routing
- Multi-stage Dockerfile for backend (deps, test, runner stages)
- Comprehensive error handling middleware with structured JSON error responses
- Request logging middleware with sensitive header masking
- Pydantic schemas with validation for search requests (min/max question length, k range)
- Collection clearing before re-ingestion to prevent data contamination
- 305 unit tests covering controllers, services, routes, schemas, middleware, and config
- 31 manual test cases for search quality and guardrail validation
- API documentation with curl examples (`docs/api-curl-examples.md`)
- Postman collection for API testing (`docs/postman/`)
- Architecture diagram in README using Mermaid
- SVG banner and screenshot for README
- Makefile with 18 commands for setup, Docker, database, execution, testing, and utilities
- Environment configuration via `.env` and `configs/` directory (no hardcoded secrets)
