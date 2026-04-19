# API Endpoint Catalog

## 1) Purpose

Single catalog of platform APIs required for Phase 1 execution and gate validation.

## 2) Conventions

- All secured endpoints require tenant-scoped claims.
- All write endpoints require request_id for traceability.
- Idempotent operations require idempotency_key.

## 3) Identity and Session

- POST /api/v1/auth/login
- POST /api/v1/auth/refresh
- POST /api/v1/auth/logout
- GET /api/v1/auth/me

## 4) Tenant and Organization

- POST /api/v1/platform/tenants
- PATCH /api/v1/platform/tenants/{tenantId}
- GET /api/v1/platform/tenants/{tenantId}
- POST /api/v1/tenant/{tenantId}/org/config
- GET /api/v1/tenant/{tenantId}/org/summary

## 5) Connector Management

- POST /api/v1/connectors/{connectorType}/configure
- POST /api/v1/connectors/{connectorType}/validate
- GET /api/v1/connectors/{connectorType}/health
- GET /api/v1/connectors/{connectorType}/capabilities

## 6) Authoring and Track Management

- POST /api/v1/authoring/generate-from-url
- GET /api/v1/authoring/tracks/{trackId}
- PUT /api/v1/authoring/tracks/{trackId}/competencies
- PUT /api/v1/authoring/tracks/{trackId}/hint-policy
- POST /api/v1/authoring/tracks/{trackId}/publish

## 7) Batch and Assignment Lifecycle

- POST /api/v1/batches
- GET /api/v1/batches/{batchId}
- POST /api/v1/batches/{batchId}/assign-track
- POST /api/v1/batches/{batchId}/release
- POST /api/v1/batches/{batchId}/close

## 8) Candidate Workspace

- GET /api/v1/candidate/home
- GET /api/v1/attempts/{attemptId}
- POST /api/v1/workspace/events
- POST /api/v1/interventions/realtime
- POST /api/v1/submissions
- GET /api/v1/submissions/{submissionId}

## 9) Scoring and Integrity

- POST /api/v1/scoring/evaluate
- GET /api/v1/scoring/{submissionId}
- GET /api/v1/integrity/{submissionId}

## 10) Evaluator Workflows

- GET /api/v1/evaluator/queue
- GET /api/v1/evaluator/review/{submissionId}
- POST /api/v1/evaluator/review/{submissionId}/decision
- POST /api/v1/evaluator/review/{submissionId}/override

## 11) LMS Outcome Sync

- POST /api/v1/lms/outcomes/push
- GET /api/v1/lms/outcomes/{submissionId}/status
- POST /api/v1/lms/outcomes/retry

## 12) Results and Certification

- POST /api/v1/results/releases
- POST /api/v1/certificates/issue
- POST /api/v1/certificates/revoke
- GET /api/v1/certificates/verify/{certificateId}

## 13) MIS and Exports

- GET /api/v1/mis/cohorts
- GET /api/v1/mis/skills
- GET /api/v1/mis/operations
- POST /api/v1/mis/exports

## 14) Simulator APIs

- POST /sim/v1/scenarios/create
- POST /sim/v1/scenarios/{scenarioId}/run
- POST /sim/v1/scenarios/{scenarioId}/replay
- DELETE /sim/v1/scenarios/{scenarioId}/purge
- GET /sim/v1/scenarios/{scenarioId}/status
- GET /sim/v1/scenarios/{scenarioId}/report

## 15) Endpoint Gate Mapping

- Latency gate: /api/v1/interventions/realtime
- Hint policy gate: /api/v1/interventions/realtime, /api/v1/workspace/events
- Claim guard gate: all secured endpoints
- Data governance gate: simulator endpoints and all ingestion paths
