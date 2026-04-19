# Environment Matrix

## 1) Purpose

Define environment responsibilities, data policy, and validation scope.

## 2) Environments

## Local Development
- Purpose: fast feature iteration and unit testing
- Data policy: synthetic test fixtures allowed only inside test harness
- Connector mode: stub or sandbox

## Integration
- Purpose: service-to-service and connector integration tests
- Data policy: tenant-scoped synthetic datasets with scenario tags
- Connector mode: Moodle sandbox

## Pre-Production
- Purpose: release candidate and gate validation
- Data policy: simulator-generated datasets only
- Connector mode: certified connector path

## Production
- Purpose: live tenant operation
- Data policy: no mock runtime data, simulator access restricted
- Connector mode: tenant-configured live connectors

## 3) Required Components by Environment

- API gateway
- orchestrator services
- intervention services
- runner services
- connector services
- observability stack
- simulator service (not user-facing runtime path)

## 4) Gate Validation by Environment

- Local: unit/component checks
- Integration: contract and claim guard checks
- Pre-production: full gate validation G1 to G4
- Production: continuous monitoring and canary safeguards

## 5) Promotion Criteria

- Local to Integration:
  - unit and component tests pass
- Integration to Pre-production:
  - connector and claim tests pass
- Pre-production to Production:
  - pressure-point gates pass
  - release sign-off approved

## 6) Access Controls

- production access limited by least privilege roles
- simulator execution in production requires explicit operator role and approval
- emergency access sessions are time-bounded and audited
