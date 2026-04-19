# Data Retention and Governance Policy

## 1) Policy Goals

- Preserve evidence required for assessment auditability.
- Minimize long-term storage of sensitive data.
- Maintain strict separation of synthetic and real datasets.

## 2) Data Classes

- Class A: identity and tenant metadata
- Class B: submissions, scores, competency outcomes
- Class C: edit traces and dialogue events
- Class D: audit logs and security events
- Class E: simulator synthetic records

## 3) Retention Windows (initial)

- Class A: retain while tenant active plus legal hold requirements
- Class B: retain for academic or hiring policy period
- Class C: retain shorter operational window unless flagged for review
- Class D: retain per security compliance requirements
- Class E: retain by scenario policy; purge by default after demo window

## 4) Governance Controls

- All records include tenant_id.
- Synthetic data includes simulation_source and scenario_id.
- Deletion and purge operations produce immutable audit entries.
- Role-based access controls govern visibility by data class.

## 5) Purge and Archive Rules

- Regular archival job for cold artifacts.
- Scenario purge endpoint removes all linked synthetic artifacts.
- Legal hold flag prevents deletion for designated records.

## 6) Data Access Reviews

- Monthly review of privileged access.
- Quarterly audit of cross-tenant report usage.
- Immediate review after any security incident.

## 7) Compliance and Evidence

Required evidence for audits:
- retention schedule configuration snapshot
- purge execution reports
- access review logs
- synthetic labeling compliance reports
