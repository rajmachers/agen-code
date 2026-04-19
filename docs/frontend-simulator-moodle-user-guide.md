# Frontend + Simulator + Moodle Testing User Guide

This guide is for demo/UAT testing across learner, admin, academic ops, and simulator capabilities, including Moodle connector APIs.

## 1) URL list

Platform URLs (local):

- Learner App (Web IDE): http://localhost:5173
- Admin Platform App: http://localhost:5174
- Academic Ops App: http://localhost:5175
- Orchestrator API docs: http://localhost:8000/docs
- Simulator service docs: http://localhost:8020/docs
- Moodle UI (container): http://localhost:8081

## 2) Credentials and access model

### A) Fast demo mode (recommended for local testing)

- Set `AUTH_ENABLED=false` in `.env`.
- No login token is required.
- Backend uses a development super admin context (`dev-user`) so tenant/bootstrap actions are available.

### B) Strict auth mode (Keycloak)

- Set `AUTH_ENABLED=true` and Keycloak env values in `.env`.
- Use a bearer token and tenant header on secured APIs:
  - `Authorization: Bearer <access_token>`
  - `x-tenant-id: <tenant_id>`

### C) Demo tenant users seeded by script

For each tenant (`tenant-acme`, `tenant-nova`, `tenant-orbit`), these user IDs are created with roles:

- `<tenant>-admin`: `tenant_admin`, `teacher`, `reviewer`, `integration_manager`
- `<tenant>-teacher`: `teacher`, `candidate`
- `<tenant>-ops`: `integration_manager`, `evaluator`

Note:

- In strict mode, role enforcement comes from token claims. The seeded user-role registry is primarily for demo visibility and admin surfaces.

## 3) One-command demo seeding

Run:

- `bash scripts/seed_demo_tenants_connectors.sh`

Optional:

- `bash scripts/seed_demo_tenants_connectors.sh http://localhost:8000`

If strict auth is enabled, export token first:

- `export ACCESS_TOKEN='<token>'`
- `bash scripts/seed_demo_tenants_connectors.sh http://localhost:8000`

What gets seeded:

1. Three demo tenants
2. Three role-bound users per tenant
3. Moodle connector profile per tenant in simulator connector registry

## 4) Frontend testing journeys

### A) Admin Platform app (`http://localhost:5174`)

Objective: tenant governance and role administration.

1. Open app and optionally paste bearer token (strict mode only).
2. Create a tenant or list existing tenants.
3. Upsert tenant user roles.
4. List tenant users.
5. Check metering for tenant.
6. Use impersonated tenant view for validation.

Expected:

- Tenant CRUD + role operations return success.
- Metering returns limits and usage windows.

### B) Academic Ops app (`http://localhost:5175`)

Objective: context bridge and evidence flows.

1. Set tenant and token (strict mode only).
2. Generate Context Bridge draft.
3. Submit draft for review and approve it.
4. Ingest evidence events.
5. Replay evidence timeline and verify flags.
6. Run ghost persona (`cheater`) and validate flags.

Expected:

- Draft moves: `draft` -> `in_review` -> `approved`.
- Evidence replay and ghost run return behavior flags.

### C) Learner app + Simulator Test Console (`http://localhost:5173`)

Objective: learner assessment + simulator/connector lifecycle.

Learning tab:

1. Generate learning module.
2. Run assessment.
3. Trigger Return to LMS handover payload.

Simulator tab:

1. Set tenant/scenario context.
2. Create scenario from template.
3. Run/status/report/replay/pause/resume.
4. Load sample connector JSON and configure.
5. List/get/delete connector by tenant.
6. Purge scenario.

Expected:

- Scenario lifecycle endpoints complete.
- Connector lifecycle endpoints complete.

## 5) Moodle real API connector capabilities (orchestrator)

These are tenant-scoped APIs for real Moodle integration paths:

- `POST /connectors/moodle/catalogue/lookup`
- `POST /connectors/moodle/users/lookup`
- `POST /connectors/moodle/cohorts/lookup`
- `POST /connectors/moodle/courses/provision`
- `POST /connectors/moodle/cohorts/sync-course`
- `POST /connectors/moodle/publish`
- `GET /connectors/moodle/publish/history`
- `GET /connectors/moodle/publish/history/{request_id}`

Typical workflow:

1. Lookup course catalogue.
2. Lookup users/cohorts.
3. Dry-run provision (`dry_run=true`).
4. Dry-run cohort sync.
5. Publish workflow call and review history records.
6. Commit mode (`dry_run=false`) once validated.

## 6) Recommended test sequence (end-to-end)

1. Bring up stack with orchestrator + frontends + simulator + moodle.
2. Run demo seed script.
3. Validate Admin Platform governance actions.
4. Validate Academic Ops authoring/evidence/ghost actions.
5. Validate Learner + Simulator lifecycle actions.
6. Validate Moodle connector dry-run APIs via `/docs`.

## 7) Troubleshooting

- `401 Missing bearer token`:
  - provide `ACCESS_TOKEN` and retry.
- `403 Cross-tenant access denied`:
  - token tenant claims do not include provided tenant.
- `403 Insufficient role privileges`:
  - token roles missing required route roles.
- Moodle connector call errors:
  - verify `MOODLE_BASE_URL` and `MOODLE_TOKEN` in `.env`.
  - verify Moodle web service functions are enabled for token user.
