# Connector Certification Checklist

## 1) Scope

This checklist certifies an LMS connector before tenant activation.

## 2) Pre-Certification Inputs

- Connector implementation version
- Supported contract version
- Tenant test credentials
- Sandbox LMS endpoint
- Test roster and course fixtures

## 3) Mandatory Certification Tests

## Launch and Identity
- CERT-CONN-001: signature validation
- CERT-CONN-002: nonce replay protection
- CERT-CONN-003: role mapping normalization
- CERT-CONN-004: malformed launch payload rejection

## Claims and Tenancy
- CERT-CONN-010: tenant_id required in all connector requests
- CERT-CONN-011: tenant mismatch rejection
- CERT-CONN-012: audit log includes request_id and actor context

## Curriculum and Activity Sync
- CERT-CONN-020: course and module mapping accuracy
- CERT-CONN-021: activity state transitions (publish/open/close)
- CERT-CONN-022: idempotent event handling with event_id

## Outcome and Competency Sync
- CERT-CONN-030: score split payload acceptance
- CERT-CONN-031: competency tag sync
- CERT-CONN-032: evidence reference persistence
- CERT-CONN-033: retry with idempotency_key on transient failure

## Health and Observability
- CERT-CONN-040: health endpoint correctness
- CERT-CONN-041: capability discovery correctness
- CERT-CONN-042: latency metrics exposed (p50, p95)

## 4) Pass Criteria

- 100 percent mandatory tests pass.
- No severity-1 or severity-2 defects open.
- Retry and idempotency tests stable across 3 consecutive runs.

## 5) Certification Outcome

- status: certified or rejected
- certified_contract_version
- certified_at
- expiry_review_date
- known_limitations

## 6) Re-Certification Triggers

- Connector major version update
- LMS API breaking change
- Contract major version change
- Security incident involving connector path
