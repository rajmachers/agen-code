# Test Strategy and Traceability Matrix

## 1) Test Objectives

- Validate end-to-end role journeys.
- Enforce pressure-point controls as release gates.
- Guarantee tenant isolation and auditability.
- Verify simulator-only synthetic data generation policy.

## 2) Test Pyramid

- Unit tests:
  - claim parsing, policy guards, scoring logic, hint budget counters, payload schema validation.
- Component tests:
  - connector adapter behavior, intervention service, replay builder, LMS payload mapper.
- Integration tests:
  - API + DB + queue + connector interactions with tenant claims.
- End-to-end tests:
  - full role flows across super admin, tenant admin, instructor, candidate, evaluator, MIS, certification.
- Non-functional tests:
  - latency, load, resilience, security negative tests.

## 3) Pressure-Point Gate Tests

## Gate 1: Latency SLA
- Test IDs:
  - LAT-001 intervention p50 under nominal pilot load.
  - LAT-002 intervention p95 under peak expected load.
  - LAT-003 fallback behavior when model response delay exceeds threshold.
- Pass criteria:
  - p50 < 2s.
  - p95 <= approved threshold.
  - fallback path activates and preserves user workflow.

## Gate 2: Hint Fade-Out
- Test IDs:
  - HINT-001 practice mode allows configured budget.
  - HINT-002 interview mode reduced budget enforced.
  - HINT-003 exam mode hard cap and denied event logging.
  - HINT-004 mode transition does not reset cap unexpectedly.
- Pass criteria:
  - Server-side budgets always authoritative.
  - denied requests include rationale and audit event.

## Gate 3: Claim Guards
- Test IDs:
  - CLAIM-001 missing tenant claim rejected at gateway.
  - CLAIM-002 tenant mismatch rejected in service layer.
  - CLAIM-003 cross-tenant artifact access blocked.
  - CLAIM-004 cross-tenant queue event consumption blocked.
- Pass criteria:
  - 100 percent rejection for cross-tenant negative tests.
  - all denials logged with actor and correlation id.

## 4) Feature Traceability Matrix

| Requirement | Ticket IDs | Test IDs | Evidence Artifact |
|---|---|---|---|
| Connector contract and onboarding | PLAT-001, PLAT-011 | CONN-001, CONN-002, CONN-003 | Connector health report |
| Tenant lifecycle and audit | PLAT-010 | TEN-001, TEN-002 | Tenant audit event log |
| Claim guard enforcement | SEC-010 | CLAIM-001, CLAIM-002, CLAIM-003, CLAIM-004 | Security test report |
| Candidate workspace shell | UI-020 | UI-001, UI-002, UI-003 | UX checklist run |
| Tier-1 intervention latency | AI-020, PERF-020 | LAT-001, LAT-002, LAT-003 | SLA dashboard snapshot |
| Edit trace ingestion and replay | TRACE-020, EVAL-040 | TRACE-001, TRACE-002 | Replay trace pack |
| Binary-Plus scoring | SCORE-030 | SCORE-101, SCORE-102 | Scoring reproducibility report |
| Process integrity | INTEG-030 | INT-001, INT-002 | Integrity evidence bundle |
| Hint fade-out policy | AI-031, TEST-030 | HINT-001, HINT-002, HINT-003, HINT-004 | Policy conformance report |
| Zero-shot authoring | AUTH-040 | AUTH-001, AUTH-002 | Track generation output pack |
| Competency publish and LMS sync | AUTH-041, LMS-040 | LMS-001, LMS-002, LMS-003 | LMS sync verification report |
| Simulator orchestration | SIM-050, SIM-051 | SIM-001, SIM-002 | Scenario run report |
| Replay and purge | SIM-052 | SIM-003, SIM-004 | Replay and purge audit report |
| Simulation labeling compliance | GOV-050 | GOV-001, GOV-002 | Synthetic labeling compliance report |
| MIS dashboards and exports | MIS-060, MIS-061 | MIS-001, MIS-002 | Analytics export validation report |
| Certification lifecycle | CERT-060 | CERT-001, CERT-002 | Certificate verification report |
| One-click full demo run | QA-060 | E2E-001 | Demo run transcript |

## 5) Environment Strategy

- Local development:
  - fast feedback for unit/component tests, mock external dependencies allowed only inside test harness.
- Integration environment:
  - real connector stubs, shared queues, tenant-scoped test data.
- Pre-production:
  - full stack including model runtime and connector health checks.
- Production:
  - synthetic scenario execution only through Simulator Service controls.

## 6) Data Policy Test Controls

- DAT-001: Product services reject unlabeled synthetic ingestion paths.
- DAT-002: Simulator-generated records include simulation_source and scenario_id.
- DAT-003: Purge removes all scenario-linked synthetic artifacts.
- DAT-004: Product runtime contains no hardcoded mock dataset fixture routes.

## 7) Automation and CI Gates

- Required on every merge:
  - unit and component suites
  - security static checks
  - claim guard regression tests
- Required on milestone close:
  - integration and end-to-end packs
  - latency benchmark run
  - policy conformance and compliance reports

## 8) Release Blocking Conditions

- Intervention p50 latency at or above 2 seconds.
- Any failing claim-guard negative test.
- Any exam-mode hint budget bypass.
- Any unlabeled synthetic records in product runtime datasets.
- Missing traceability artifact for a closed milestone requirement.

## 9) Reporting Cadence

- Daily:
  - gate health summary (latency, claims, hint policy).
- Weekly:
  - requirement-to-test traceability status and defect trend.
- Milestone close:
  - signed release evidence packet with all gate reports attached.
