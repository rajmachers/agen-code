# Phase 1 Implementation Runbook

## 1) Scope

Phase 1 target:
- Deliver Moodle-based connector onboarding
- Deliver candidate workspace with active shadowing
- Deliver Binary-Plus scoring path and LMS sync
- Deliver simulator MVP for reproducible demo setup

## 2) Daily Operating Loop

### 09:00
- Cross-lane standup
- Review blocked dependencies and gate metrics

### 12:00
- Integration checkpoint
- Verify connector health and claim guard failure counts

### 16:00
- SLA check
- Intervention latency dashboard review

### 18:00
- Build and release candidate status
- Update open risk list and owner actions

## 3) Mandatory Dashboards

- Intervention latency: p50, p95, p99
- Claim guard violations by endpoint
- Connector health by tenant
- LMS sync success and retries
- Simulator run success and purge integrity

## 4) Phase 1 Work Packages

## WP1 Connector Onboarding
- Implement tenant connector setup UI and API
- Run connector certification tests
- Enable Moodle reference connector for first tenant

Completion check:
- Tenant can onboard via config only
- Connector health status remains green for 24h window

## WP2 Candidate Workspace Core
- Deliver Monaco shell and role route guards
- Integrate intervention channel
- Capture edit trace and dialogue events

Completion check:
- Candidate can complete first assessment attempt end-to-end
- Workspace event stream validated with replay ids

## WP3 Scoring and LMS Outcome Sync
- Enable Binary-Plus scoring
- Attach evidence refs and integrity flags
- Sync competency payload to Moodle

Completion check:
- LMS receives competency-rich payload
- Idempotent retry behavior verified

## WP4 Simulator MVP
- Build quick demo scenario
- Build scenario reporting and purge
- Enforce synthetic tagging

Completion check:
- One command creates demo tenant and sample batch
- Purge removes all scenario-linked synthetic data

## 5) Release Gates

### Gate G1 Latency
- Intervention p50 < 2 seconds
- Alert policy configured and tested

### Gate G2 Hint Policy
- Exam mode hint cap cannot be bypassed
- Denied hint events are logged and auditable

### Gate G3 Claim Guard
- Cross-tenant access tests fail as expected
- Tenant claim required for all secured routes

### Gate G4 Data Governance
- No mock fixture data paths in product services
- All simulator records tagged

## 6) Escalation Protocol

- G1 breach: SRE lead incident owner, ML lead and backend lead responders
- G2 breach: ML lead owner, QA lead blocks release until retest
- G3 breach: Security lead owner, release freeze automatic
- G4 breach: Platform lead owner, purge and policy correction before proceed

## 7) Handoff Artifacts at Phase 1 Close

- Connector certification report
- Latency SLA report
- Claim guard security report
- LMS payload validation report
- Simulator execution and purge report
- Release readiness sign-off record

## 8) Definition of Phase 1 Done

Phase 1 is done only when:
- all four gates pass for two consecutive weekly cycles
- one full role journey demo runs through simulator without manual patching
- tenant onboarding requires configuration only, no code changes
