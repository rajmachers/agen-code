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
   - Learner App (Web IDE): http://localhost:5173
   - Admin Platform App: http://localhost:5174
   - Academic Ops App: http://localhost:5175

## Frontend Demo URLs, Seeded Access, and Real User Walkthrough

Use this section for a fast end-to-end demo with realistic user journeys.

### 1) Bring up stack and seed demo tenants

1. Start services:
   - `docker compose -f infra/docker-compose.yml up -d --build orchestrator runner simulator web-ide admin-platform academic-ops moodle`
2. Seed demo tenants, users, and simulator connector profiles:
   - `bash scripts/seed_demo_tenants_connectors.sh`

### 2) Complete frontend URL list

- Learner App (Web IDE): `http://localhost:5173`
- Admin Platform App: `http://localhost:5174`
- Academic Ops App: `http://localhost:5175`
- Orchestrator API docs: `http://localhost:8000/docs`
- Simulator service docs: `http://localhost:8020/docs`
- Moodle UI: `http://localhost:8081`

### 3) Credentials and seeded identities

Fast demo mode (default local path):

- Set `AUTH_ENABLED=false` in `.env`.
- No login/password is needed in frontend apps.
- Backend uses a development super admin context:
  - super admin identity: `dev-user`
  - effective role: `super_admin`

Strict auth mode (Keycloak):

- Set `AUTH_ENABLED=true` and valid Keycloak env values.
- Provide:
  - `Authorization: Bearer <access_token>`
  - `x-tenant-id: <tenant_id>`
- Note: this repo seeds tenant user IDs and roles for demo data, but it does not seed Keycloak passwords.

Seeded tenant users (created by `scripts/seed_demo_tenants_connectors.sh`):

- Tenants: `tenant-acme`, `tenant-nova`, `tenant-orbit`
- Per-tenant users:
  - `<tenant>-admin`: `tenant_admin`, `teacher`, `reviewer`, `integration_manager`
  - `<tenant>-teacher`: `teacher`, `candidate`
  - `<tenant>-ops`: `integration_manager`, `evaluator`

### 4) Real demo walkthrough (role-based scenarios)

Scenario A: Platform super admin journey (Admin Platform App)

1. Open `http://localhost:5174`.
2. In fast mode, leave token empty.
3. Click `Load My Identity` and confirm super admin access.
4. Click `List Tenants` and verify seeded tenants are visible.
5. Pick `tenant-acme`, assign/update roles for a user, then click `List Tenant Users`.
6. Click `Get Metering` to show limits and usage.
7. Click `Impersonated Tenant View` for tenant-scoped admin story.

Scenario B: Academic operations journey (Academic Ops App)

1. Open `http://localhost:5175`.
2. Set tenant to `tenant-acme`.
3. Click `Load Identity` (token optional in fast mode).
4. Generate a Context Bridge draft, then run:
   - `Submit Review`
   - `Approve Draft`
5. In Evidence Player:
   - ingest sample events
   - replay timeline
6. Run ghost persona (`cheater`) and show behavior flags.

Scenario C: Learner and simulation journey (Learner App)

1. Open `http://localhost:5173`.
2. Learning tab:
   - generate module
   - evaluate submission
   - run `Return to LMS (Handover Guard)`
3. Simulator Test Console tab:
   - set tenant/scenario context
   - create from template
   - run/status/report/replay/pause/resume
   - configure/list/get/delete connector profile
   - purge scenario

### 5) Simulation quick-demo checklist (features to test)

Use this in front of stakeholders for a 10-15 minute quick demo:

1. Scenario lifecycle: create -> run -> status -> report -> replay.
2. Runtime control: pause -> resume.
3. Connector lifecycle: configure -> list -> get -> delete.
4. Tenant isolation check:
   - run with `tenant-acme`
   - switch to another tenant and confirm scoped behavior.
5. Cleanup: purge scenario and show deterministic re-run from template.

### 6) Optional backend validation commands for the demo host

- Moodle connector readiness:
  - `bash scripts/check_moodle_readiness.sh http://localhost:8000 tenant-acme /tmp/moodle_readiness_demo`
- Moodle connector UAT:
  - `bash scripts/run_moodle_connector_uat.sh http://localhost:8000 tenant-acme /tmp/moodle_uat_demo`

For the longer guide, see `docs/frontend-simulator-moodle-user-guide.md`.

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

## End-to-end execution smoke script

Run the newly implemented admin -> authoring -> evidence -> ghost -> handover flow in one command:

- `bash scripts/smoke_execution_flow.sh`

Optional arguments:

- base URL (default `http://localhost:8000`)
- tenant ID (default generated timestamped tenant)

Example:

- `bash scripts/smoke_execution_flow.sh http://localhost:8000 tenant_smoke_manual_01`

## End-to-end execution smoke script (strict auth mode)

Run the same execution flow with Keycloak-enabled auth (`AUTH_ENABLED=true`) and tenant header enforcement.

Prerequisites:

- export `ACCESS_TOKEN` with a valid bearer token
- set tenant ID as arg2 or export `TENANT_ID`
- token must include tenant + role claims needed by authoring/evidence/ghost/delivery routes

Usage:

- `bash scripts/smoke_execution_flow_auth.sh http://localhost:8000 tenant_a`

The script sends both headers on all secured calls:

- `Authorization: Bearer <token>`
- `x-tenant-id: <tenant_id>`

## Guided Simulator Testing UI (click-based)

The Web IDE now includes a managed **Simulator Test Console** tab so you can run simulation testing with guided clicks, notes, and sample payload autofill.

1. Open Web IDE: `http://localhost:5173`
2. Click `Simulator Test Console`
3. Follow the numbered cards in order:
   - Step 1: Set tenant/scenario context
   - Step 2: Create from template (quick path)
   - Step 3: Optional custom scenario JSON (autoload sample)
   - Step 4: Run, status, report, replay, pause, resume
   - Step 5: Connector configure/list/get/delete with sample JSON
   - Step 6: Purge scenario cleanup

Notes:
- The interface calls orchestrator endpoints under `/simulator/*`.
- Sample scenario and connector payloads are preloaded via one-click buttons.
- Action logs and JSON outputs are shown inline for quick validation during QA.

## Running Orchestrator Tests

Some orchestrator tests import from the top-level `app` package, so run pytest from `services/orchestrator` with `PYTHONPATH=.` set.

Examples:

- `cd services/orchestrator && PYTHONPATH=. pytest tests/test_moodle_clients.py -q`
- `cd services/orchestrator && PYTHONPATH=. pytest -q`

## Suggested next production steps

- Add secure container isolation for untrusted code (Firecracker/gVisor)
- Replace in-memory queue with Redis/Celery or NATS-based workers
- Add plagiarism and anomaly models with explainable flags
- Add observability stack (OpenTelemetry + Prometheus + Grafana)

## Authentication and Authorization (Keycloak)

The orchestrator now supports Keycloak-backed authentication and tenant-scoped authorization.

1. Enable auth in `.env`:
   - `AUTH_ENABLED=true`
   - Set `KEYCLOAK_BASE_URL`, `KEYCLOAK_REALM`, `KEYCLOAK_CLIENT_ID`, `KEYCLOAK_CLIENT_SECRET`
2. Send bearer token on secured APIs:
   - `Authorization: Bearer <access_token>`
3. For tenant-scoped connector APIs, include tenant header:
   - `x-tenant-id: <tenant_id>`

Role model:

- `super_admin`: platform-wide access across tenants
- `tenant_admin`: full access within assigned tenant(s)
- `integration_manager`: connector and simulator operations in assigned tenant(s)
- `teacher`, `sme`, `candidate`, `evaluator`: module-specific access

Auth identity endpoint:

- `GET /auth/me`
  - Returns subject, username, roles, tenant assignments, and module access flags for frontend routing.

Tenant isolation:

- Tenant users are blocked from cross-tenant requests (403).
- Super admin can operate across tenants.

## Execution APIs for 3-App Strategy

The backend now includes implementation-first APIs aligned with the approved 3-app rollout and phase gates.

Admin Platform APIs:

- `POST /admin/tenants` tenant provisioning
- `GET /admin/tenants` global/tenant list mode
- `POST /admin/tenants/{tenant_id}/users/{user_id}/roles` tenant role assignment
- `GET /admin/tenants/{tenant_id}/users` tenant user-role listing
- `POST /admin/impersonate` super admin impersonated tenant view
- `GET /admin/tenants/{tenant_id}/metering` quota/metering status

Academic Ops APIs:

- `POST /authoring/context-bridge/generate` Context Bridge (URL/README ingestion)
- `GET /authoring/drafts/{draft_id}` draft retrieval
- `POST /authoring/drafts/{draft_id}/submit-review` review transition
- `POST /authoring/drafts/{draft_id}/approve` approval transition
- `POST /evidence/sessions` evidence ingest
- `GET /evidence/sessions/{session_id}/replay` Evidence Player replay + flags

Learner / Delivery APIs:

- `POST /delivery/handover/return-to-lms` Handover Guard with competency payload validation

Ghost User Simulation APIs:

- `POST /simulator/personas/run` persona-driven API-level event generation (`expert`, `struggler`, `cheater`)

These endpoints are tenant-scoped and RBAC-protected using Keycloak claims when `AUTH_ENABLED=true`.

## Frontend App Surfaces (3-App Strategy)

- `web-ide` (Learner app): Monaco workspace, assessment feedback, and LMS handover guard.
- `frontend/admin-platform` (Admin Platform app): tenant provisioning, role assignment, impersonation, metering.
- `frontend/academic-ops` (Academic Ops app): context bridge generation, draft review flow, evidence replay, ghost personas.

To start all frontend surfaces with backend in one command:

- `docker compose -f infra/docker-compose.yml up -d --build orchestrator web-ide admin-platform academic-ops`

## Program Tracking Baseline

For detailed enterprise requirements, app/system feature mapping, phased roadmap, 4-gate done criteria, and weekly tracking templates, use:

- `docs/enterprise-requirements-and-phased-plan.md`
