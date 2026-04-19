# Simulator App PRD

## 1) Product Objective

Build a dedicated Simulator App that creates realistic end-to-end platform data for demos, QA, load testing, and analytics validation without introducing mock data logic into product services.

## 2) Non-Goals

- No direct writes to production tables bypassing platform APIs.
- No hidden simulator hooks inside runtime user-facing services.
- No untagged synthetic records.

## 3) Users and Jobs

### Demo operations user
- Bootstrap a demo tenant and full story in minutes.

### QA and release user
- Run deterministic seeded scenarios before milestone sign-off.

### Data and analytics user
- Replay historical batches to validate dashboards and trend logic.

### Sales engineering user
- Produce customer-specific demo data packs with configurable complexity.

## 4) Functional Requirements

## 4.1 Scenario Builder
- Select scenario template
- Configure tenant and batch sizes
- Set pedagogy profile and mode mix
- Define timeline speed (real-time or accelerated)

## 4.2 Execution Engine
- Provision tenant and connector config through APIs
- Create courses, modules, and activities
- Enroll personas and assign roles
- Generate attempts, traces, submissions, and outcomes
- Trigger LMS sync and evaluator queue population

## 4.3 Replay Engine
- Replay completed scenario by scenario_id
- Rebuild timelines in accelerated mode
- Compare run deltas for regression tracking

## 4.4 Purge and Reset
- Purge by scenario_id
- Reset tenant simulation assets only
- Verify no orphan synthetic records remain

## 4.5 Compliance Guardrails
- simulation_source and scenario_id mandatory on every created record
- soft and hard delete support based on policy
- simulator action audit logs with actor and request_id

## 5) Scenario Packs

### Pack A: Quick Demo
- 1 tenant, 1 course, 1 batch, 30 candidates
- full role journey in under 10 minutes

### Pack B: Academic Cohort
- semester timeline, remediation branches, competency progression

### Pack C: Hiring Assessment
- timed assessments, evaluator queues, shortlisting signals

### Pack D: Integrity Stress
- mixed normal and suspicious behavior patterns

### Pack E: Latency Load
- high-concurrency intervention and submission pressure

### Pack F: Historical Replay
- rehydrate prior synthetic batches for MIS trend views

## 6) System Architecture

- Simulator UI and API
- Scenario Orchestrator
- Seeded Data Generator
- Connector Runner
- Replay Worker
- Purge Worker
- Compliance Validator

Persistence:
- scenario metadata store
- execution run logs
- synthetic record index for purge and audits

## 7) API Surface (Simulator Only)

- POST /sim/v1/scenarios/create
- POST /sim/v1/scenarios/{scenarioId}/run
- POST /sim/v1/scenarios/{scenarioId}/replay
- POST /sim/v1/scenarios/{scenarioId}/pause
- POST /sim/v1/scenarios/{scenarioId}/resume
- DELETE /sim/v1/scenarios/{scenarioId}/purge
- GET /sim/v1/scenarios/{scenarioId}/status
- GET /sim/v1/scenarios/{scenarioId}/report

## 8) Acceptance Criteria

- One-click run can create a complete role journey demo.
- All synthetic records are labeled and queryable by scenario_id.
- Purge workflow deletes all synthetic artifacts reliably.
- Re-running same seed yields stable distribution outcomes.
- No product service contains hardcoded mock fixtures.

## 9) NFRs

- Run visibility: live progress and error state in UI
- Reliability: recover from connector transient failures
- Scalability: support concurrent scenario runs per tenant
- Security: simulator access limited to authorized operator roles

## 10) Release Plan

### Release 1
- scenario builder, quick demo pack, run and report

### Release 2
- replay engine, purge engine, historical pack

### Release 3
- load pack, regression compare, scheduled runs

## 11) Risks and Mitigation

- Risk: synthetic data pollutes production analytics permanently
  - Mitigation: tagging and purge validation checks

- Risk: connector failures make scenarios flaky
  - Mitigation: retry backoff and explicit connector diagnostics

- Risk: scenario drift from real product behavior
  - Mitigation: run via public APIs and continuous contract alignment
