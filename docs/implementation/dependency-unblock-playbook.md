# Dependency Unblock Playbook

## 1) Purpose

Resolve cross-lane blockers within 48 hours to protect critical path continuity.

## 2) Blocker Classification

- Type A: Contract ambiguity
- Type B: API dependency unavailable
- Type C: Environment instability
- Type D: Security/compliance gate pending
- Type E: Performance regression

## 3) Unblock Workflow

1. Raise blocker with ticket id and impacted milestone.
2. Assign blocker owner and backup owner.
3. Define workaround path within 4 hours.
4. Execute unblock session with impacted lanes.
5. Rebaseline ETA and update command center.

## 4) Time Targets

- Triage start: within 2 hours
- Workaround decision: within 4 hours
- Resolution target: within 48 hours

## 5) Escalation Rules

- If unresolved by 24 hours:
  - escalate to architecture lead and product lead
- If unresolved by 48 hours:
  - escalate to program steering and enforce scope trade decision

## 6) Scope Trade Framework

When blocker threatens milestone close:
- Preserve gate-critical items
- Defer non-critical UX enhancements
- Defer optional analytics enrichments
- Never defer claim guard, hint cap, or latency gate work

## 7) Blocker Report Template

- Blocker ID:
- Origin ticket:
- Impacted tickets:
- Impacted milestone:
- Root cause:
- Chosen workaround:
- Owner:
- ETA:
- Escalation status:
