# Capacity and Cost Plan (Phase 1 to Phase 2)

## 1) Purpose

Provide initial sizing and cost controls for pilot and early production operation.

## 2) Capacity Inputs

- Active tenants in pilot: 2 to 5
- Concurrent candidates during peak windows: 100 to 300
- Intervention requests per active candidate per hour: 10 to 30
- Submission events per candidate per day: 1 to 5

## 3) Service Capacity Baseline

## API and orchestration
- target: 300 to 500 req/min sustained
- scale strategy: horizontal replicas with request queue buffering

## Tier-1 intervention service
- primary load driver for latency
- target: keep p50 under 2 seconds at pilot peak
- scale strategy: dedicated inference workers and prompt budget controls

## Runner service
- submission spikes near deadlines
- scale strategy: queue-backed worker pool with bounded execution slots

## Connector service
- outcome sync and roster updates
- scale strategy: retry queues, idempotency, and connector circuit breaker

## Simulator service
- keep isolated from product runtime resources
- run in scheduled windows when possible

## 4) Cost Drivers

- model inference compute for real-time interventions
- runner compute for test execution
- storage for traces and artifacts
- observability and log retention
- connector traffic and retries

## 5) Cost Controls

- enforce intervention prompt compaction
- route deep analysis to async lower-priority workers
- archive old traces based on retention policy
- cap simulator concurrent scenario runs
- use autoscaling floors and ceilings with schedule-aware policies

## 6) Pilot Budget Guardrails

- define weekly run-rate ceiling by environment
- alert when spend forecast exceeds 80 percent of weekly budget
- require approval for temporary overprovisioning

## 7) Scale Readiness Triggers

Move to Phase 2 scaling posture when:
- intervention p95 degrades in two consecutive peak windows
- queue lag exceeds accepted threshold in peak periods
- connector retry backlog grows across two reporting cycles

## 8) Reporting

Weekly report should include:
- capacity utilization by service
- SLA performance versus load
- cost per active candidate
- top three optimization opportunities
