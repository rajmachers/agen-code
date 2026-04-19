# Partner LMS Onboarding Playbook

## 1) Objective

Onboard a new LMS partner adapter using the existing connector contract and certification process.

## 2) Entry Criteria

- Connector contract v1 accepted by partner team.
- Partner sandbox endpoint available.
- Auth credentials and role mapping details available.

## 3) Onboarding Phases

## Phase A: Discovery and Mapping
- Collect partner LMS identity fields.
- Map course/module/activity semantics.
- Validate launch protocol compatibility.

## Phase B: Adapter Configuration
- Configure connector endpoints and auth.
- Configure role and context mappings.
- Run capability discovery check.

## Phase C: Certification
- Run full connector certification checklist.
- Resolve failures and rerun until pass.
- Publish certified contract version and limitations.

## Phase D: Pilot Tenant Activation
- Activate connector for pilot tenant only.
- Run simulator quick demo scenario.
- Validate outcome sync and competency mapping.

## 4) Required Artifacts

- connector config snapshot
- certification report
- known limitations list
- rollback plan
- pilot sign-off

## 5) Common Failure Patterns

- Role mapping mismatch causing access errors
- Course context field mismatch causing wrong activity links
- Outcome payload schema mismatch causing sync failure
- Token expiry and refresh misconfiguration

## 6) Operational Handover

- Add connector to monitoring dashboards
- Add connector-specific runbook notes
- Add partner escalation contacts
- Schedule re-certification checkpoint

## 7) Exit Criteria

- Connector certified with no critical defects
- Pilot tenant passes role journey UAT
- Pressure-point gates unaffected by new adapter
- Steering approval for broader tenant rollout
