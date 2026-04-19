# Integrated Coding Practice and Assessment Engine

This repository provides an MVP implementation of an AI-powered coding practice and assessment platform integrated with Moodle LMS.

## What is implemented

- A clear architecture and requirements digest in `docs/`
- Docker-based runtime with Moodle, database, Ollama, and backend services
- Orchestration API (FastAPI) for:
  - Learning content generation
  - Submission evaluation dispatch
  - Moodle progress sync hooks
- Assessment runner service for secure test execution and metrics extraction
- Simulator service for scenario-driven demo and synthetic data workflows
- Moodle local plugin scaffold for LTI/API interoperability
- Monaco-based web IDE shell with API integration points

## High-level flow

1. Learner opens coding activity in Moodle.
2. Moodle launches the IDE via LTI or deep-link.
3. IDE pulls assignment metadata and starter repo.
4. Learner codes in Monaco and commits to a workspace repo.
5. Submission is sent to orchestration API.
6. Runner executes tests in sandbox, captures correctness/performance.
7. AI feedback is generated using local Ollama-hosted coding model.
8. Results are pushed back to Moodle gradebook and adaptive-path signals.

## Quick start

1. Copy `.env.example` to `.env` and adjust values.
2. Start stack:
   - `docker compose -f infra/docker-compose.yml up --build`
3. Pull model in Ollama container:
   - `docker exec -it ollama ollama pull qwen2.5-coder:7b`
4. Open:
   - Moodle: http://localhost:8081
   - API docs: http://localhost:8000/docs
   - Simulator docs: http://localhost:8020/docs
   - Web IDE: http://localhost:5173

## Assessment feedback modes

The assessment endpoint supports a runtime mode switch through the `mode` query parameter:

- `deterministic` (default): fastest path, uses deterministic 3-line feedback.
- `llm`: forces Ollama-based feedback generation.
- `auto`: follows server config (`assessment_use_ollama`) for fallback behavior.

Examples:

- Deterministic (low latency):
   - `curl -sS -X POST 'http://localhost:8000/assessment/evaluate?mode=deterministic' -H 'Content-Type: application/json' -d '{"assignment_id":"a1","learner_id":"u1","language":"python","repo_url":"https://example.com/repo.git","commit_hash":"abc123","tests_path":"tests"}'`

- LLM (higher latency, model-generated text):
   - `curl -sS -X POST 'http://localhost:8000/assessment/evaluate?mode=llm' -H 'Content-Type: application/json' -d '{"assignment_id":"a1","learner_id":"u1","language":"python","repo_url":"https://example.com/repo.git","commit_hash":"abc123","tests_path":"tests"}'`

## Benchmark script

Run comparative medians for assessment deterministic mode, assessment llm mode, and learning:

- `bash scripts/benchmark_modes.sh`

Optional arguments:

- base URL (default `http://localhost:8000`)
- run count (default `5`)

Example:

- `bash scripts/benchmark_modes.sh http://localhost:8000 7`

## Suggested next production steps

- Add secure container isolation for untrusted code (Firecracker/gVisor)
- Replace in-memory queue with Redis/Celery or NATS-based workers
- Add SSO/OAuth2 + signed LTI 1.3 launch validation
- Add plagiarism and anomaly models with explainable flags
- Add observability stack (OpenTelemetry + Prometheus + Grafana)
