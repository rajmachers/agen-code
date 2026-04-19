# Sprint Execution Board: AI Coding Platform

## 1) Planning Rules

- Delivery mode: back-to-back milestones with no phase overlap unless dependencies are cleared.
- Release gate rule: if any pressure point fails, milestone cannot close.
- Pressure points:
  - Latency SLA: Tier 1 intervention p50 < 2s.
  - Hint Fade-Out: mode-specific budgets strictly enforced.
  - Claim Guards: tenant isolation on every secured request path.

## 2) Team Lanes and Ownership

- Lane A: Platform Core
  - tenant lifecycle, claim guards, connector registry
- Lane B: Workspace and AI
  - Monaco shell, intervention pipeline, fade-out engine
- Lane C: Learning and Assessment Ops
  - authoring, competency sync, evaluator workflows
- Lane D: Simulator and Insights
  - simulator orchestration, MIS population, replay/testing
- Cross-Lane: SRE and Security
  - observability, SLA gating, security testing, release approval

## 3) Milestone Backlog (Ticket Level)

## M0: Control Plane Freeze (Week 1)

### Tickets
1. PLAT-001 Define connector contract v1 (LMS launch, context, outcomes, health).
- Owner: Lane A
- Dependencies: none
- DoD:
  - Connector schema approved by product and architecture.
  - Validation test list published.

2. SEC-001 Finalize claim schema and request guard policy.
- Owner: Lane A + Cross-Lane
- Dependencies: none
- DoD:
  - Required claims documented: tenant_id, org_id, actor_id, role.
  - Gateway and service guard strategy signed off.

3. SCORE-001 Freeze Binary-Plus schema and evidence contract.
- Owner: Lane C
- Dependencies: none
- DoD:
  - Score payload fields locked.
  - Evidence references standardized.

4. SIM-001 Freeze no-mock-data policy and simulator boundaries.
- Owner: Lane D
- Dependencies: none
- DoD:
  - Policy published and accepted.
  - Simulator-only generation policy enforced in architecture docs.

## M1: Tenant and Connector Foundation (Weeks 2-3)

### Tickets
1. PLAT-010 Build tenant lifecycle APIs.
- Owner: Lane A
- Dependencies: SEC-001
- DoD:
  - create/suspend/archive/restore APIs implemented.
  - Audit events emitted for each state transition.

2. PLAT-011 Implement connector registry and tenant configuration store.
- Owner: Lane A
- Dependencies: PLAT-001
- DoD:
  - Tenant can configure Moodle connector details.
  - Health checks show connector readiness states.

3. SEC-010 Enforce claim guards in API middleware and DB access wrappers.
- Owner: Lane A + Cross-Lane
- Dependencies: SEC-001
- DoD:
  - All secured endpoints reject missing tenant claims.
  - Automated cross-tenant negative tests pass.

4. OPS-010 Add connector and tenancy observability baseline.
- Owner: Cross-Lane
- Dependencies: PLAT-010, PLAT-011
- DoD:
  - Dashboard includes tenant API errors and connector health by tenant.

## M2: Candidate Workspace and Tier 1 Intervention (Weeks 4-6)

### Tickets
1. UI-020 Build candidate shell routes and Monaco workspace primitives.
- Owner: Lane B
- Dependencies: PLAT-010
- DoD:
  - activity bar, explorer, tabs, problems panel, source control panel available.

2. AI-020 Implement real-time intervention service with fast model tier.
- Owner: Lane B
- Dependencies: UI-020
- DoD:
  - Intervention returns actionable response under SLA in pilot load profile.

3. TRACE-020 Implement workspace event ingestion (edits/dialogue).
- Owner: Lane B
- Dependencies: UI-020
- DoD:
  - Event stream includes attempt_id, tenant_id, scenario-safe metadata.

4. PERF-020 Build latency dashboard and alerting for intervention path.
- Owner: Cross-Lane
- Dependencies: AI-020
- DoD:
  - p50, p95, p99 visible by tenant and mode.
  - SLA breach alerts active.

## M3: Scoring, Integrity, and Hint Fade-Out (Weeks 7-8)

### Tickets
1. SCORE-030 Implement Binary-Plus scoring service.
- Owner: Lane C
- Dependencies: SCORE-001, TRACE-020
- DoD:
  - baseline_score and insight_score computed and persisted.

2. INTEG-030 Implement process-aware integrity engine.
- Owner: Lane C
- Dependencies: TRACE-020
- DoD:
  - Integrity flags generated from trace and progression evidence.

3. AI-031 Implement mode-aware hint budget and fade-out policy.
- Owner: Lane B
- Dependencies: AI-020
- DoD:
  - practice/interview/exam budgets configurable.
  - exam mode hard caps enforced server-side.

4. TEST-030 Add policy conformance tests for hint fade behavior.
- Owner: Cross-Lane
- Dependencies: AI-031
- DoD:
  - budget bypass attempts fail.
  - transition tests pass.

## M4: Instructor, Evaluator, and Competency Sync (Weeks 9-10)

### Tickets
1. AUTH-040 Build zero-shot authoring flow from URL.
- Owner: Lane C
- Dependencies: PLAT-011
- DoD:
  - Instructor can generate track and preview outputs.

2. AUTH-041 Build competency mapping and publish workflow.
- Owner: Lane C
- Dependencies: AUTH-040
- DoD:
  - Published track includes competency tags and thresholds.

3. EVAL-040 Build evaluator queue and evidence replay UI.
- Owner: Lane C + Lane B
- Dependencies: INTEG-030
- DoD:
  - Evaluator can review trace replay and submit decision.

4. LMS-040 Implement Moodle competency-rich payload sync.
- Owner: Lane A + Lane C
- Dependencies: AUTH-041, SCORE-030
- DoD:
  - Payload includes score splits, skill tags, evidence refs.
  - Retry and failure diagnostics implemented.

## M5: Simulator MVP and Demo Automation (Weeks 11-12)

### Tickets
1. SIM-050 Build simulator run orchestrator and scenario schema.
- Owner: Lane D
- Dependencies: SIM-001
- DoD:
  - Scenario can create demo tenant, course, batch, learners.

2. SIM-051 Build simulation generators (attempts, submissions, evaluator events).
- Owner: Lane D
- Dependencies: SIM-050
- DoD:
  - Synthetic cohorts generated via simulator APIs only.

3. SIM-052 Add historical replay and scenario reset/purge.
- Owner: Lane D
- Dependencies: SIM-051
- DoD:
  - Replay works for at least one completed batch.
  - purge removes scenario-linked data safely.

4. GOV-050 Add synthetic data labeling and compliance checks.
- Owner: Cross-Lane + Lane D
- Dependencies: SIM-051
- DoD:
  - All simulated records include simulation_source and scenario_id.

## M6: MIS, Results, and Certification (Weeks 13-14)

### Tickets
1. MIS-060 Build cohort and operational dashboards.
- Owner: Lane D
- Dependencies: SIM-051, LMS-040
- DoD:
  - dashboards show cohort progress, skill heatmaps, latency indicators.

2. MIS-061 Build export scheduler and data packaging.
- Owner: Lane D
- Dependencies: MIS-060
- DoD:
  - CSV/API export jobs run with tenant scope.

3. CERT-060 Build results release and certificate lifecycle.
- Owner: Lane C + Lane D
- Dependencies: LMS-040
- DoD:
  - release window controls active.
  - issue/revoke/verify flows available.

4. QA-060 Build end-to-end demo script using simulator.
- Owner: Lane D + Cross-Lane
- Dependencies: SIM-052, CERT-060
- DoD:
  - one-click reproducible demo journey validated.

## 4) Milestone Gate Checklist

## Gate A: Latency SLA
- Intervention p50 < 2s.
- Intervention p95 within approved threshold.
- Alerting + fallback strategy active.

## Gate B: Hint Fade-Out
- Mode budgets enforced server-side.
- Exam mode cannot exceed assistance caps.
- Audit trail for hint decisions available.

## Gate C: Claim Guard
- Cross-tenant read/write blocked at gateway and service layer.
- Queue and artifact scoping include tenant boundaries.
- Security negative tests pass.

## 5) Weekly Operating Rhythm

1. Monday: scope lock + gate criteria confirmation.
2. Daily: cross-lane 30-minute integration standup.
3. Wednesday: telemetry checkpoint (latency, guard failures, connector health).
4. Friday: milestone readiness review with go/no-go decision.

## 6) Definition of Ready (DoR)

A ticket starts only if:
- API contract exists.
- Tenant and role rules are defined.
- Acceptance test conditions are written.
- Observability hooks are identified.

## 7) Definition of Done (DoD) Global

A ticket closes only if:
- Functional acceptance criteria pass.
- Security and tenancy checks pass.
- Metrics and logs are emitted.
- Documentation and runbook are updated.

## 8) Launch Readiness Criteria

- Full role journey works end-to-end: super admin -> tenant admin -> instructor -> candidate -> evaluator -> MIS -> certification.
- No product service depends on hardcoded mock data.
- Simulator can regenerate a complete demo tenant in one command.
- Pressure-point gates pass in pilot environment for two consecutive weeks.
