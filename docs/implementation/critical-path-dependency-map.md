# Critical Path Dependency Map

## 1) Objective

Identify sequence-critical work that directly affects Phase 1 go-live.

## 2) Critical Path (CP)

CP-1 Contract Freeze:
- PLAT-001 -> SEC-001 -> SCORE-001

CP-2 Tenancy Foundation:
- SEC-001 -> PLAT-010 -> SEC-010

CP-3 Connector Activation:
- PLAT-001 -> PLAT-011 -> LMS-040

CP-4 Workspace and SLA:
- PLAT-010 -> UI-020 -> AI-020 -> PERF-020

CP-5 Scoring and Integrity:
- TRACE-020 -> SCORE-030 -> INTEG-030

CP-6 Hint Policy:
- AI-020 -> AI-031 -> TEST-030

CP-7 Authoring to Outcome Closure:
- PLAT-011 -> AUTH-040 -> AUTH-041 -> LMS-040

CP-8 Demo Readiness:
- SIM-001 -> SIM-050 -> SIM-051 -> SIM-052 -> QA-060

## 3) Dependency Risks

- Delay in SEC-001 blocks all guarded implementation.
- Delay in AI-020 blocks latency gate validation.
- Delay in LMS-040 blocks competency closure and pilot readiness.
- Delay in SIM-050 blocks reproducible demos and analytics proof.

## 4) Mitigation Actions

- Assign backup owner for each CP anchor ticket.
- Start test scaffolding one sprint earlier for CP-4/CP-6.
- Reserve hardening buffer at end of every milestone.
- Run twice-weekly dependency unblock session.

## 5) Visual (Mermaid)

```mermaid
flowchart LR
  A[PLAT-001 Contract v1] --> B[SEC-001 Claims Policy]
  B --> C[PLAT-010 Tenant Lifecycle]
  C --> D[SEC-010 Guard Enforcement]

  A --> E[PLAT-011 Connector Registry]
  E --> F[AUTH-040 Zero-shot Authoring]
  F --> G[AUTH-041 Competency Publish]
  G --> H[LMS-040 Competency Sync]

  C --> I[UI-020 Candidate Workspace]
  I --> J[AI-020 Realtime Intervention]
  J --> K[PERF-020 SLA Dashboards]
  J --> L[AI-031 Hint Fade-out]
  L --> M[TEST-030 Policy Tests]

  I --> N[TRACE-020 Event Ingestion]
  N --> O[SCORE-030 Binary-Plus]
  O --> P[INTEG-030 Integrity Engine]

  Q[SIM-001 Simulator Policy] --> R[SIM-050 Scenario Orchestrator]
  R --> S[SIM-051 Synthetic Cohorts]
  S --> T[SIM-052 Replay and Purge]
  T --> U[QA-060 One-click Demo]

  H --> V[Phase 1 Close]
  K --> V
  M --> V
  D --> V
  U --> V
```

## 6) Phase 1 Close Conditions (Critical Path Complete)

- G1 latency gate passing
- G2 hint policy gate passing
- G3 claim guard gate passing
- LMS competency closure verified
- One-click simulator demo validated
