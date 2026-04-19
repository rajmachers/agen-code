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

## Troubleshooting

Use these checks when strict-auth mode fails:

1. Verify orchestrator health:
	 - `curl -sS http://localhost:8000/health`
2. Verify token is accepted:
	 - `curl -sS -H "Authorization: Bearer $ACCESS_TOKEN" http://localhost:8000/auth/me`
3. Verify tenant scoping header path:
	 - `curl -sS -H "Authorization: Bearer $ACCESS_TOKEN" -H "x-tenant-id: $TENANT_ID" http://localhost:8000/auth/me`

Common failures:

- `401 Missing bearer token` or `Token validation failed`:
	- token is missing/expired, or Keycloak introspection config is incorrect.
- `403 Cross-tenant access denied`:
	- token tenant claims do not include the provided `TENANT_ID`.
- `403 Insufficient role privileges`:
	- token roles do not include required roles for authoring/evidence/ghost/delivery endpoints.
