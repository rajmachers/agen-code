# Customer Demo Run Script

## 1) Demo Goal

Show a complete planner-to-doer learning loop with evidence-based assessment and LMS closure.

## 2) Pre-Demo Checklist

- Simulator scenario is prepared and validated.
- Connector health status is green.
- Latency dashboard is visible.
- UAT critical scripts are passed.

## 3) Demo Flow

1. Super admin view
- Create or select tenant.
- Show connector configuration and health.

2. Tenant admin view
- Show batch setup and role provisioning.

3. Instructor view
- Use zero-shot authoring from source URL.
- Publish competency-mapped assessment.

4. Candidate view
- Open VS Code-like workspace.
- Show active shadowing interventions.
- Submit attempt and review score split.

5. Evaluator view
- Open replay trace and dialogue progression.
- Show decision and rationale logging.

6. LMS closure
- Show competency-rich payload reflected in LMS.

7. MIS and certification
- Show cohort analytics.
- Issue and verify certificate.

## 4) Talking Points

- Connector-first architecture avoids LMS lock-in.
- Process-aware integrity evaluates how code was built, not only final output.
- Binary-Plus scoring balances trust and insight.
- Simulator guarantees reproducible demos and QA without mock runtime data.

## 5) Demo Failure Recovery

- If connector fails:
  - Switch to validated backup tenant and rerun scenario.
- If latency spikes:
  - Enable fallback intervention profile and continue flow.
- If sync delay occurs:
  - Show retry queue and idempotent recovery.

## 6) Demo Completion Checklist

- Role journey completed end-to-end.
- Pressure-point dashboards shown.
- Competency sync evidence shown.
- Questions captured with follow-up owners.
