# Architecture and Technology Choices

## Chosen stack

- LMS: Moodle (open source, mature plugin ecosystem)
- Model hosting: Ollama (local, self-hosted models)
- Coding model default: Qwen2.5-Coder 7B (upgrade path to larger models)
- API layer: FastAPI (typed contracts, async I/O)
- Runner: Python worker service with sandbox contract
- IDE frontend: React + Monaco Editor
- Version control: GitHub/GitLab integration using PAT/OAuth app
- Queue (MVP): in-process background task
- Queue (production): Redis + Celery/NATS
- Data stores (production recommendation):
  - PostgreSQL for attempts/grades/analytics
  - Object storage for artifacts/logs

## Core services

- Web IDE service:
  - embeds Monaco
  - assignment fetch, local editing, commit/push controls
  - AI chat/autocomplete bridge
- Orchestrator API:
  - assignment generation
  - dispatch evaluation jobs
  - compose AI feedback from test evidence
  - sync results to Moodle
- Runner service:
  - secure execution contract
  - test run, timeout, memory and CPU collection
- Moodle plugin:
  - launch endpoints
  - gradebook sync
  - adaptive path hooks
- Ollama:
  - local model inferencing for content + feedback

## Sequence overview

1. Instructor creates or auto-generates assignment in Moodle.
2. Learner launches IDE activity.
3. Learner submits commit hash.
4. Orchestrator calls runner with repo + tests.
5. Runner returns verdict + metrics.
6. Orchestrator asks Ollama for feedback narrative.
7. Orchestrator posts graded payload to Moodle plugin endpoint.
8. Moodle updates gradebook and recommends next modules.

## Security architecture

- Submission sandboxing with resource limits.
- Signed service-to-service tokens.
- Sanitized prompt and output filters.
- Full audit logs for grading decisions.
