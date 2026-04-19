# Pilot Rollout Plan

## 1) Pilot Objectives

- Validate end-to-end product value in real workflows.
- Prove pressure-point gates under live usage.
- Collect evidence for customer readiness and scale plan.

## 2) Pilot Cohort Design

- Tenants: 2
- Batches per tenant: 2
- Candidates per batch: 30 to 50
- Instructors per tenant: 2
- Evaluators per tenant: 2

## 3) Pilot Phases

## Phase P1: Dry Run (Week 1)
- Use simulator to create baseline data.
- Validate onboarding and connector sync.
- Run UAT script set.

## Phase P2: Controlled Live (Weeks 2-3)
- Enable real users with practice mode first.
- Monitor intervention SLA and hint behavior.
- Run daily command center.

## Phase P3: High-Stakes Mode Trial (Week 4)
- Enable exam mode for selected assessments.
- Validate fade-out enforcement and integrity outputs.
- Run evaluator workload test.

## Phase P4: Outcomes and Review (Week 5)
- Review competency gains and sync quality.
- Measure operational KPIs and incident trends.
- Produce go/no-go decision for broader rollout.

## 4) Pilot KPI Targets

- Intervention p50 < 2 seconds
- Claim guard violations accepted: 0
- LMS sync success >= 99 percent
- First-task completion median < 5 minutes
- Evaluator turnaround within target SLA

## 5) Pilot Risks and Controls

- Risk: SLA degradation under load
  - Control: fallback templates and worker scale-out

- Risk: connector instability
  - Control: retry and idempotency replay queue

- Risk: policy confusion among users
  - Control: role-based onboarding checklists and in-product guidance

## 6) Pilot Exit Criteria

- All pressure-point gates pass for two consecutive weeks.
- No unresolved Sev1 incidents.
- Customer-facing demo can be reproduced by simulator script.
- Approved rollout recommendation signed by product, security, and engineering.
