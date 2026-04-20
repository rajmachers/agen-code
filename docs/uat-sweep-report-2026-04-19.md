# UAT Sweep Report - 2026-04-19

This report captures a full backend/API UAT sweep aligned to the three frontend apps, simulator lifecycle, and Moodle connector API surface.

## Environment

- Base API: http://localhost:8000
- Learner app: http://localhost:5173
- Admin app: http://localhost:5174
- Academic Ops app: http://localhost:5175
- Simulator docs: http://localhost:8020/docs
- API docs: http://localhost:8000/docs

Run artifacts:

- Output directory: `/tmp/uat_sweep`
- UAT tenant: `tenant_uat_1776619725`
- UAT scenario: `scenario_uat_1776619725`

## Result Summary

### URL reachability

- Web IDE: 200
- Admin Platform: 200
- Academic Ops: 200
- Orchestrator docs: 200
- Simulator docs: 200

### Admin flow

- `POST /admin/tenants`: 200
- `POST /admin/tenants/{tenant}/users/{user}/roles`: 200
- `GET /admin/tenants/{tenant}/users`: 200
- `GET /admin/tenants/{tenant}/metering`: 200

### Academic Ops flow

- `POST /authoring/context-bridge/generate`: 200
- `POST /authoring/drafts/{draft_id}/submit-review`: 200
- `POST /authoring/drafts/{draft_id}/approve`: 200
- `POST /evidence/sessions`: 200
- `GET /evidence/sessions/{session_id}/replay`: 200
- `POST /simulator/personas/run`: 200

### Learner flow endpoints

- `POST /learning/generate`: 200
- `POST /assessment/evaluate?mode=deterministic`: 200
- `POST /delivery/handover/return-to-lms`: 200

### Simulator lifecycle

- `GET /simulator/scenarios/templates`: 200
- `POST /simulator/scenarios/templates/quick_demo`: 200
- `POST /simulator/scenarios/{scenario}/run`: 200
- `GET /simulator/scenarios/{scenario}/status`: 200
- `GET /simulator/scenarios/{scenario}/report`: 200
- `POST /simulator/scenarios/{scenario}/pause`: 200
- `POST /simulator/scenarios/{scenario}/resume`: 200
- `POST /simulator/scenarios/{scenario}/replay`: 200
- `DELETE /simulator/scenarios/{scenario}/purge`: 200

### Simulator connector lifecycle

- `GET /simulator/connectors`: 200
- `POST /simulator/connectors/configure` (UAT tenant): 200
- `GET /simulator/connectors/{tenant}` (UAT tenant): 200

### Moodle connector API surface

- `POST /connectors/moodle/catalogue/lookup`: 400
  - Error: `MOODLE_TOKEN is not configured`
- `POST /connectors/moodle/publish` (dry_run=true): 200
  - Status payload: `failed`
  - Failure reason in steps: `MOODLE_TOKEN is not configured`

## Assessment

- Platform app pathways and simulator capabilities are testable and operational in local mode.
- Moodle connector routes are wired and reachable, but real Moodle actions are blocked by missing connector credential configuration (`MOODLE_TOKEN`).

## Required to pass Moodle real-API UAT

1. Configure valid `MOODLE_BASE_URL` and `MOODLE_TOKEN` in `.env`.
2. Ensure token user has required web service functions in Moodle.
3. Re-run connector tests:
   - `POST /connectors/moodle/catalogue/lookup`
   - `POST /connectors/moodle/users/lookup`
   - `POST /connectors/moodle/cohorts/lookup`
   - `POST /connectors/moodle/courses/provision` (`dry_run=true`, then `false`)
   - `POST /connectors/moodle/cohorts/sync-course`
   - `POST /connectors/moodle/publish`

## References

- Frontend + simulator guide: `docs/frontend-simulator-moodle-user-guide.md`
- Demo seed script: `scripts/seed_demo_tenants_connectors.sh`
- UAT sweep script: `scripts/run_uat_sweep.sh`

## Delta Re-run (post connector auto-configure hardening)

Re-run command:

- `./scripts/run_uat_sweep.sh http://localhost:8000 /tmp/uat_sweep_latest`

Observed code deltas versus the earlier run:

- `GET /simulator/connectors/{tenant}` moved from 404 to 200 for the fresh UAT tenant.
- `POST /simulator/connectors/configure` now runs inside the sweep and returns 200.

Current status after hardening:

- All platform, admin, authoring, delivery, evidence, simulator, and connector lifecycle calls: 200.
- Moodle real API dependency remains the only blocker:
  - `POST /connectors/moodle/catalogue/lookup`: 400 (`MOODLE_TOKEN is not configured`)
  - `POST /connectors/moodle/publish` (dry-run): HTTP 200 envelope with internal failed step due to missing token.

Artifacts for this re-run:

- `/tmp/uat_sweep_latest`
- `/tmp/uat_sweep_latest/status_matrix.txt`

## Final Credential Snapshot (latest run)

Latest verification (final-check attempt) confirms the same blocker state:

- `MOODLE_BASE_URL`: set in running orchestrator
- `MOODLE_TOKEN`: not set to real value (`replace-me`/empty state)
- `POST /connectors/moodle/catalogue/lookup`: 400
- Response detail: `MOODLE_TOKEN is not configured`

Fast readiness check command:

- `bash scripts/check_moodle_readiness.sh http://localhost:8000 tenant-acme /tmp/moodle_readiness`

When readiness output shows `TOKEN_SET=true` and `CATALOGUE_CODE=200`, run the final green retest:

- `bash scripts/run_moodle_connector_uat.sh http://localhost:8000 tenant-acme /tmp/moodle_uat_final`
- `bash scripts/run_uat_sweep.sh http://localhost:8000 /tmp/uat_sweep_final`

## Retry Update (2026-04-20)

Commands executed:

- `bash scripts/check_moodle_readiness.sh http://localhost:8000 tenant-acme /tmp/moodle_readiness_final`
- `bash scripts/run_moodle_connector_uat.sh http://localhost:8000 tenant-acme /tmp/moodle_uat_final`
- `bash scripts/run_uat_sweep.sh http://localhost:8000 /tmp/uat_sweep_final`

Observed results:

- Readiness:
  - `BASE_SET=true`
  - `TOKEN_SET=false`
  - `CATALOGUE_CODE=400`
  - `READY=false`
- Moodle connector UAT:
  - `health`: 200
  - `catalogue`: 400
  - detail: `MOODLE_TOKEN is not configured`
- Full UAT sweep (`/tmp/uat_sweep_final/status_matrix.txt`):
  - platform/admin/authoring/evidence/delivery/simulator/connector lifecycle: 200
  - `moodle_catalogue`: 400
  - `moodle_publish`: 200 (envelope), internal failed step due to missing token

Conclusion remains unchanged: platform flows are operational; real Moodle API pass is blocked only by unresolved `MOODLE_TOKEN` configuration.
