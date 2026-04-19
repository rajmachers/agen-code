# Smoke Execution Flows

This repo provides two end-to-end smoke scripts for the execution strategy routes.

## 1) Non-auth flow

Use this when auth is disabled (`AUTH_ENABLED=false`, default local dev mode).

Run:

- `bash scripts/smoke_execution_flow.sh`

Optional args:

- `base_url` (default: `http://localhost:8000`)
- `tenant_id` (default: generated `tenant_smoke_<timestamp>`)

Example:

- `bash scripts/smoke_execution_flow.sh http://localhost:8000 tenant_smoke_manual_01`

Validates this path:

1. `/admin/tenants`
2. `/admin/tenants/{tenant_id}/users/{user_id}/roles`
3. `/authoring/context-bridge/generate`
4. `/authoring/drafts/{draft_id}/submit-review`
5. `/authoring/drafts/{draft_id}/approve`
6. `/evidence/sessions`
7. `/evidence/sessions/{session_id}/replay`
8. `/simulator/personas/run`
9. `/delivery/handover/return-to-lms`

## 2) Strict-auth flow

Use this when auth is enabled (`AUTH_ENABLED=true`) with Keycloak token validation.

Prerequisites:

- export `ACCESS_TOKEN` with a valid bearer token
- provide tenant via arg2 or export `TENANT_ID`
- token claims must include tenant + route roles

Run:

- `bash scripts/smoke_execution_flow_auth.sh http://localhost:8000 tenant_a`

Headers sent on all requests:

- `Authorization: Bearer <access_token>`
- `x-tenant-id: <tenant_id>`

## Notes

- Both scripts fail fast on non-200 responses and print the failing payload.
- Summary output prints tenant, draft status, evidence flags, ghost flags, and handover status.
- Temporary artifacts are written under `/tmp/smoke_*.json`.
