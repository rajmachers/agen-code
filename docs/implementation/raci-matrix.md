# RACI Matrix by Milestone

## Legend
- R: Responsible
- A: Accountable
- C: Consulted
- I: Informed

## Roles
- PL: Product Lead
- AL: Architecture Lead
- BL: Backend Lead
- FL: Frontend Lead
- ML: ML Engineer Lead
- SL: Security Lead
- SREL: SRE Lead
- QAL: QA Lead
- IL: Integrations Lead
- DL: Data and Insights Lead
- SIML: Simulator Lead

## M0 Control Plane Freeze
| Workstream | PL | AL | BL | FL | ML | SL | SREL | QAL | IL | DL | SIML |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Connector contract v1 | C | A | R | I | I | C | I | I | R | I | I |
| Claim schema and guard policy | I | C | R | I | I | A | C | C | I | I | I |
| Binary-Plus schema | A | C | C | I | R | I | I | C | C | I | I |
| Simulator boundary policy | C | C | I | I | I | C | I | C | I | I | A/R |

## M1 Tenant and Connector Foundation
| Workstream | PL | AL | BL | FL | ML | SL | SREL | QAL | IL | DL | SIML |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Tenant lifecycle APIs | I | C | A/R | I | I | C | C | C | I | I | I |
| Connector registry and config | I | C | R | I | I | C | I | I | A/R | I | I |
| Claim middleware and DB guards | I | C | R | I | I | A | C | C | I | I | I |
| Tenancy observability | I | I | C | I | I | C | A/R | I | I | C | I |

## M2 Workspace and Tier-1 Intervention
| Workstream | PL | AL | BL | FL | ML | SL | SREL | QAL | IL | DL | SIML |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Candidate workspace shell | C | I | C | A/R | C | I | I | C | I | I | I |
| Real-time intervention service | I | C | C | C | A/R | I | C | C | I | I | I |
| Edit trace ingestion | I | I | A/R | C | C | C | I | C | I | I | I |
| Latency dashboards and alerts | I | I | C | I | C | C | A/R | C | I | I | I |

## M3 Scoring Integrity Fade-Out
| Workstream | PL | AL | BL | FL | ML | SL | SREL | QAL | IL | DL | SIML |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Binary-Plus scoring service | A | C | C | I | R | I | I | C | C | I | I |
| Integrity engine | C | C | R | I | C | A | I | C | I | I | I |
| Hint fade-out policy engine | C | C | C | C | A/R | C | I | C | I | I | I |
| Policy conformance tests | I | I | C | I | C | C | I | A/R | I | I | I |

## M4 Instructor Evaluator LMS Sync
| Workstream | PL | AL | BL | FL | ML | SL | SREL | QAL | IL | DL | SIML |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Zero-shot authoring flow | A | C | C | R | C | I | I | C | C | I | I |
| Competency map publish | A | C | C | C | R | I | I | C | C | I | I |
| Evaluator queue and replay | C | I | C | A/R | C | C | I | C | I | I | I |
| Moodle competency sync | I | C | R | I | C | C | I | C | A/R | I | I |

## M5 Simulator MVP
| Workstream | PL | AL | BL | FL | ML | SL | SREL | QAL | IL | DL | SIML |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Scenario orchestrator | I | C | C | I | I | I | I | C | I | I | A/R |
| Synthetic cohort generators | I | I | C | I | C | C | I | C | I | C | A/R |
| Replay and purge | I | I | C | I | I | C | I | C | I | I | A/R |
| Synthetic data compliance checks | I | I | I | I | I | A | I | C | I | C | R |

## M6 MIS Results Certification
| Workstream | PL | AL | BL | FL | ML | SL | SREL | QAL | IL | DL | SIML |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MIS dashboards | C | I | C | C | I | I | C | C | I | A/R | C |
| Export scheduler | I | I | C | I | I | C | C | C | I | A/R | I |
| Result and certificate lifecycle | C | I | A/R | C | I | C | I | C | I | C | I |
| One-click demo journey | I | I | C | I | I | I | C | A | I | C | R |

## Escalation Path
- SLA breach (latency): SREL owns incident lead, ML and BL are required responders.
- Claim guard failure: SL owns incident lead, BL required responder, release frozen.
- Hint cap breach in exam mode: ML owns hotfix lead, QAL blocks release until retested.
