# Connector Contract v1

## 1) Purpose

Define a single tenant-configurable integration contract between the coding platform and any LMS.

Current reference adapter:
- Moodle connector

Future adapters:
- Customer LMS and partner LMS implementations of the same contract

## 2) Contract Scope

Each connector implementation must provide:
- Secure launch and identity handoff
- Curriculum context mapping
- Assignment and activity state synchronization
- Outcome and competency sync
- Health checks and diagnostics
- Error/retry semantics

## 3) Domain Model

### Required identity fields
- tenant_id
- org_id
- lms_user_id
- platform_user_id
- role
- session_id

### Required learning context fields
- lms_course_id
- lms_module_id
- activity_id
- batch_id
- mode (practice, interview, exam)
- launch_timestamp

### Required outcome fields
- overall_score
- baseline_score
- insight_score
- skills_mastered
- skills_needing_support
- evidence_refs
- integrity_flags
- evaluated_at

## 4) Interface Definitions

## 4.1 Launch

### Endpoint (connector adapter)
- POST /connector/v1/launch/resolve

### Input
- signed launch payload from LMS (LTI 1.3 or equivalent)

### Output
- normalized platform launch context

### Validation rules
- signature validation mandatory
- nonce replay protection mandatory
- mode must be one of allowed enum values

## 4.2 Enrollment Sync

### Endpoint
- POST /connector/v1/enrollments/sync

### Input
- list of roster changes

### Output
- accepted, skipped, failed counts with error details

### Idempotency
- required using event_id

## 4.3 Activity State Sync

### Endpoint
- POST /connector/v1/activities/state

### Input
- assignment published, opened, closed, extended, archived events

### Output
- state transition result and version

## 4.4 Outcome Sync

### Endpoint
- POST /connector/v1/outcomes/push

### Input
- competency-rich outcome payload

### Output
- sync status and target record id

### Retry semantics
- connector must support safe retries with idempotency_key

## 4.5 Health and Capability Discovery

### Endpoints
- GET /connector/v1/health
- GET /connector/v1/capabilities

### Health response fields
- status
- auth_status
- schema_version
- last_successful_sync_at
- latency_ms_p50
- latency_ms_p95

### Capabilities response fields
- launch_supported
- roster_sync_supported
- competency_sync_supported
- result_release_supported

## 5) Security and Claims

Mandatory for every inbound/outbound call:
- tenant_id claim
- actor_id claim
- role claim
- request_id correlation id

Mandatory controls:
- token expiry and rotation
- payload signature validation
- strict tenant partition enforcement
- immutable audit log for launch and sync events

## 6) Error Model

Standard error object:
- code
- message
- retriable
- retry_after_seconds
- details

Error classes:
- AUTH_FAILURE
- CLAIM_MISSING
- TENANT_MISMATCH
- SCHEMA_INVALID
- RATE_LIMITED
- DEPENDENCY_UNAVAILABLE

## 7) Versioning and Compatibility

- contract_version required in each request
- backward compatible changes only in minor versions
- breaking changes require new major path

## 8) Compliance Test Suite

Minimum adapter certification tests:
- CONN-001 launch signature and nonce tests
- CONN-002 tenant claim mismatch rejection
- CONN-003 outcome sync idempotency
- CONN-004 retry behavior on transient errors
- CONN-005 capability discovery accuracy

Adapter cannot be activated for tenant onboarding unless all tests pass.
