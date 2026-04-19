# NFR and SLO Contract

## 1) Purpose

Define non-functional requirements and service-level objectives that must be met for milestone closure.

## 2) Performance SLOs

## Intervention Service
- p50 response time: < 2.0 seconds
- p95 response time: <= 4.0 seconds
- error rate: < 1.0 percent per 15-minute interval

## Submission Evaluation
- p95 end-to-end evaluation completion: <= target window per environment
- queue wait time within agreed threshold during peak windows

## Connector Sync
- outcome sync success: >= 99.0 percent
- transient retry recovery: >= 99.5 percent

## 3) Reliability Targets

- Core API availability target per environment window
- no single point of failure in intervention path
- retry and idempotency required on connector writes

## 4) Security NFRs

- tenant claim enforcement on every secured request path
- zero accepted cross-tenant leakage incidents
- immutable audit logs for privileged actions

## 5) Data Governance NFRs

- no hardcoded mock data paths in product runtime
- synthetic records always tagged
- purge and retention workflows auditable

## 6) Usability NFRs

- candidate first-task completion under target median time
- role journey completion without manual operator intervention

## 7) Observability NFRs

- dashboards for latency, claim guards, connector health, sync backlog
- alerting for all gate threshold breaches
- incident breadcrumbs via request_id and correlation_id

## 8) SLO Measurement Rules

- sample windows and percentile calculation method standardized
- exclude planned maintenance windows from availability SLO
- include degraded mode metrics with annotation

## 9) Release Gate Binding

A milestone can close only when:
- all mandatory SLOs pass in agreed validation window
- no active Sev1 incidents
- all pressure-point gates are green
