# Risk Register (Scored)

## 1) Scoring Method

- Probability (P): 1 to 5
- Impact (I): 1 to 5
- Risk Score = P x I
- Priority Bands:
  - Critical: 16 to 25
  - High: 10 to 15
  - Medium: 5 to 9
  - Low: 1 to 4

## 2) Top Risks

| Risk ID | Risk | P | I | Score | Band | Owner | Mitigation | Trigger | Contingency |
|---|---|---:|---:|---:|---|---|---|---|---|
| R-001 | Tier-1 intervention latency breaches p50 SLA | 4 | 5 | 20 | Critical | SRE Lead | tiered routing, prompt compaction, autoscale workers | p50 >= 2s for 5 min | activate fallback profile and async deep reasoning |
| R-002 | Exam-mode hint cap bypass | 3 | 5 | 15 | High | ML Lead | server-side budgets, policy tests, deny logging | unexpected hint approvals in exam mode | block exam mode and patch policy engine |
| R-003 | Cross-tenant data leakage | 2 | 5 | 10 | High | Security Lead | gateway claim enforcement, scoped repositories, negative tests | tenant mismatch alert or anomaly | freeze release and isolate endpoint |
| R-004 | Connector instability for Moodle sync | 3 | 4 | 12 | High | Integrations Lead | idempotent retries, health probes, backoff queues | sync failures > 1% | replay queue and temporary degraded mode |
| R-005 | Zero-shot generation quality variance | 3 | 4 | 12 | High | Assessment Lead | generation templates, quality checks, instructor review gate | rejection rate spike on generated tracks | require manual review and tighten templates |
| R-006 | Simulator pollutes analytics with unlabeled data | 2 | 4 | 8 | Medium | Simulator Lead | mandatory labels, compliance checks, purge test | unlabeled records detected | quarantine dataset and run purge |
| R-007 | Evaluator throughput drops due to replay complexity | 3 | 3 | 9 | Medium | Product Lead | evidence summarization and queue prioritization | queue backlog exceeds SLA | add triage mode and redistribute queues |
| R-008 | LMS competency mapping mismatch | 3 | 4 | 12 | High | Integrations Lead | mapping contract tests and schema versioning | payload validation failures | fallback mapping profile and replay sync |
| R-009 | Over-assistance causes learner dependency | 3 | 3 | 9 | Medium | Learning Lead | staged fade-out, explain-why checkpoints | high hint dependency index | tighten hint budgets by mode |
| R-010 | Partner LMS expansion delayed by adapter drift | 2 | 4 | 8 | Medium | Architecture Lead | strict connector contract certification | adapter test failures | prioritize adapter hardening sprint |

## 3) Weekly Risk Process

1. Review all Critical and High risks first.
2. Update probability and impact based on latest telemetry.
3. Record mitigation progress and owner ETA.
4. Promote/demote risk band only with evidence.
5. Escalate unresolved Critical risks to command center.

## 4) Risk Burndown Targets

- By end of Phase 1:
  - Critical risks: 0 open without active contingency
  - High risks: max 3 open with approved mitigation ETA
- By end of Phase 2:
  - No unresolved claim-guard or hint-cap bypass risk

## 5) Gate Linkage

- G1 Latency: R-001
- G2 Hint Fade-Out: R-002 and R-009
- G3 Claim Guard: R-003
- G4 Data Governance: R-006
