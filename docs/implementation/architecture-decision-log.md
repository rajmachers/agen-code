# Architecture Decision Log

## ADR-001
- Title: Hub-spoke LMS architecture
- Status: Accepted
- Decision: Keep LMS as planning hub and coding platform as execution spoke.
- Rationale: lower adoption friction, connector-based extensibility.

## ADR-002
- Title: Connector-first integration model
- Status: Accepted
- Decision: Tenant integrations via configurable connector contract.
- Rationale: avoids LMS-specific code forks.

## ADR-003
- Title: Binary-Plus scoring model
- Status: Accepted
- Decision: 70 percent deterministic baseline plus 30 percent insight score.
- Rationale: transparent trust with AI-enhanced feedback.

## ADR-004
- Title: Process-over-product integrity signals
- Status: Accepted
- Decision: use edit trace and dialogue progression in integrity evaluation.
- Rationale: stronger authenticity checks in LLM era.

## ADR-005
- Title: Tiered model inference
- Status: Accepted
- Decision: fast model for realtime intervention, deeper models async.
- Rationale: maintain sub-2-second generative experience.

## ADR-006
- Title: No mock data in product runtime
- Status: Accepted
- Decision: all synthetic data created through separate Simulator Service.
- Rationale: cleaner governance and reliable demo reproducibility.

## ADR-007
- Title: Tenant claim guard hard requirement
- Status: Accepted
- Decision: every secured path requires tenant claims and scoped data access.
- Rationale: prevent multi-tenant leakage risk.

## ADR-008
- Title: Moodle as reference connector
- Status: Accepted
- Decision: phase 1 uses Moodle adapter and certification path.
- Rationale: immediate implementation target and baseline for partner LMS.

## ADR-009
- Title: Role-based frontend cockpits
- Status: Accepted
- Decision: separate role journeys under shared shell.
- Rationale: workflow clarity and operational scale.

## ADR-010
- Title: Gate-based release progression
- Status: Accepted
- Decision: no milestone close unless pressure-point gates pass.
- Rationale: reduces regressions in critical learning and security controls.
