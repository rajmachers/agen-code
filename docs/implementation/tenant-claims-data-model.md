# Tenant and Claims Data Model

## 1) Purpose

Define mandatory tenancy and authorization data structures across API, queue, storage, and analytics paths.

## 2) Core Entities

## Tenant
- tenant_id (uuid, immutable)
- tenant_key (string, human readable)
- status (active, suspended, archived)
- connector_type (moodle, partner_lms_x)
- policy_pack_id
- created_at
- updated_at

## Organization
- org_id (uuid)
- tenant_id (fk)
- name
- domain
- sso_provider
- branding_config

## Actor
- actor_id (uuid)
- tenant_id (fk)
- org_id (fk)
- role (super_admin, tenant_admin, instructor, candidate, evaluator, mis, cert_manager)
- external_user_id
- status

## Session Claim Set
- request_id
- tenant_id
- org_id
- actor_id
- role
- scopes
- mode (practice, interview, exam, admin)
- issued_at
- expires_at

## 3) Storage Partition Rules

- Every business table includes tenant_id.
- Composite indexes must begin with tenant_id for scoped access patterns.
- Artifact object keys use path prefix:
  - /tenant/{tenant_id}/org/{org_id}/...
- Event topics/streams use tenant-scoped channels.

## 4) Required Query Guard Pattern

- Service layer must call scoped repository methods only.
- Repository methods require tenant_id parameter.
- Queries without tenant_id are blocked by lint/check policy.

## 5) Queue/Event Claim Propagation

Mandatory event envelope:
- event_id
- tenant_id
- org_id
- actor_id (if user-originated)
- correlation_id
- event_type
- payload
- timestamp

Consumer validation:
- Reject event if tenant_id missing or mismatched with subscription scope.

## 6) Analytics Segregation

- Warehouse dimensions include tenant_id and scenario_id.
- Cross-tenant reports are allowed only for super admin role and audited.
- Synthetic data records require simulation_source and scenario_id.

## 7) Security Test Controls

- CLAIM-MODEL-001: no table missing tenant_id.
- CLAIM-MODEL-002: query without tenant scope fails check.
- CLAIM-MODEL-003: artifact key path always tenant-prefixed.
- CLAIM-MODEL-004: event envelope claim validation enforced.
