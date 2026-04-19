# KPI Definitions

## 1) Purpose

Standardize KPI semantics, formulas, and ownership for delivery and operations.

## 2) Product KPIs

## First Task Completion Median
- Definition: median time from candidate first workspace open to first successful submission.
- Owner: Product Lead
- Source: workspace telemetry + submission events

## Hint Dependency Index
- Definition: hints accepted per solved task, segmented by mode.
- Owner: Learning Lead
- Source: intervention logs + completion events

## Competency Gain Rate
- Definition: percentage increase in mastered skills per learner over period.
- Owner: Assessment Lead
- Source: LMS sync payloads

## 3) Reliability KPIs

## Intervention p50 and p95
- Definition: latency percentiles for realtime intervention endpoint.
- Owner: SRE Lead
- Source: API latency metrics

## Connector Sync Success
- Definition: successful outcome syncs divided by attempted syncs.
- Owner: Integrations Lead
- Source: connector service logs

## Queue Backlog Age
- Definition: oldest unprocessed event age in critical queues.
- Owner: Platform Lead
- Source: queue telemetry

## 4) Security and Governance KPIs

## Claim Guard Violation Rate
- Definition: denied requests due to claim mismatch per total secured requests.
- Owner: Security Lead
- Source: gateway and service guard logs

## Cross-Tenant Incident Count
- Definition: confirmed multi-tenant isolation incidents in reporting window.
- Owner: Security Lead
- Target: zero

## Synthetic Label Compliance
- Definition: labeled synthetic records divided by synthetic records created.
- Owner: Simulator Lead
- Target: 100 percent

## 5) Delivery KPIs

## Milestone On-Time Rate
- Definition: milestones closed on planned date divided by total milestones.
- Owner: PMO

## Critical Blocker Resolution Time
- Definition: median time to resolve critical-path blockers.
- Owner: Architecture Lead

## Test Traceability Coverage
- Definition: backlog items linked to tests divided by total in-scope items.
- Owner: QA Lead

## 6) Reporting Cadence

- Daily: SLA and security gate KPIs
- Weekly: product and delivery KPIs
- Milestone close: full KPI scorecard with trend analysis
