# Security Threat Model

## 1) Scope

This threat model covers:
- multi-tenant APIs
- connector integration paths
- candidate workspace and intervention services
- simulator workflows
- analytics and certification paths

## 2) Security Objectives

- Prevent cross-tenant data exposure.
- Protect assessment integrity and anti-cheating controls.
- Protect identity and session boundaries.
- Ensure tamper-evident audit trails.

## 3) Assets

- Tenant data and learner submissions
- Edit traces and dialogue logs
- Scoring outputs and competency mappings
- Connector credentials and tokens
- Certificates and verification metadata

## 4) Trust Boundaries

- Boundary A: Browser to platform APIs
- Boundary B: Platform to connector adapter
- Boundary C: Platform services to model runtime
- Boundary D: Product runtime to simulator runtime
- Boundary E: Internal services to storage and queue systems

## 5) Threats and Controls (STRIDE style)

## Spoofing
Threat:
- forged actor tokens or replayed launch payloads
Controls:
- signed tokens with short TTL
- nonce replay prevention for launch requests
- step-up auth for admin and release operations

## Tampering
Threat:
- payload manipulation in connector sync or submission flow
Controls:
- request signing for sensitive integrations
- immutable audit logs for state transitions
- checksum validation for artifacts

## Repudiation
Threat:
- users deny critical actions (override, release, purge)
Controls:
- structured audit logs with actor, tenant, request_id
- mandatory rationale fields for evaluator overrides
- signed release sign-off records

## Information Disclosure
Threat:
- cross-tenant query leakage
- exposure of learner traces
Controls:
- mandatory tenant claims and scoped repositories
- data encryption in transit and at rest
- redaction for sensitive telemetry in shared dashboards

## Denial of Service
Threat:
- model inference saturation
- connector endpoint overload
Controls:
- tiered inference routing and rate limits
- queue backpressure and autoscaling
- connector retry backoff and circuit breakers

## Elevation of Privilege
Threat:
- role escalation to super admin or tenant admin capabilities
Controls:
- strict RBAC and least privilege scopes
- privileged action approval workflows
- periodic role audit and dormant account controls

## 6) Abuse Cases

- Candidate attempts to bypass exam hint cap.
- Evaluator attempts unauthorized cross-tenant review.
- Connector configured to wrong tenant endpoint.
- Simulator used to write unlabeled records.

Required checks:
- policy engine server-side hint enforcement
- tenant claim check on every evaluator query
- connector validation before activation
- synthetic data labeling validator in CI and runtime checks

## 7) Security Test Plan Mapping

- Threat tests map to CLAIM, HINT, CONN, and DAT test suites.
- Sev1 automatic release freeze on:
  - claim guard regression
n  - hint cap bypass in exam mode
  - connector auth/signature failure pattern

## 8) Incident Response Hooks

- Security incidents routed through SLA playbook.
- Mandatory 48-hour RCA and regression test addition.
- Re-certification required for affected connector path.
