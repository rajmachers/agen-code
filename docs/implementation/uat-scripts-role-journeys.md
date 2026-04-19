# UAT Scripts: Role Journeys

## 1) Objective

Validate complete user journeys across all roles with measurable pass criteria.

## 2) Script A: Super Admin to Tenant Activation

Steps:
1. Login as super admin.
2. Create new tenant and assign policy pack.
3. Enable Moodle connector and save credentials.
4. Run connector health check.

Expected:
- Tenant status changes to active.
- Connector status is healthy.
- Audit log captures actor, tenant, request_id.

## 3) Script B: Tenant Admin Setup

Steps:
1. Login as tenant admin.
2. Configure org profile and SSO settings.
3. Invite instructor, evaluator, candidate users.
4. Create first batch.

Expected:
- Users provisioned with role-scoped access.
- Batch created with calendar windows.

## 4) Script C: Instructor Authoring and Publish

Steps:
1. Open authoring studio.
2. Input source URL and generate track.
3. Map competency tags and publish.
4. Assign track to batch.

Expected:
- Track generation succeeds.
- Competency map attached to published track.
- Candidates see assigned assessment.

## 5) Script D: Candidate Workspace and Submission

Steps:
1. Candidate opens assigned assessment.
2. Works in Monaco workspace.
3. Receives active shadowing hints.
4. Submits attempt.

Expected:
- Intervention responses within SLA.
- Submission persists with evidence refs.
- Score split appears: baseline and insight.

## 6) Script E: Evaluator Review

Steps:
1. Evaluator opens queue.
2. Reviews replay trace and dialogue progression.
3. Submits decision with rationale.

Expected:
- Decision saved with audit trail.
- Override requires rationale.

## 7) Script F: LMS Sync and Competency Update

Steps:
1. Trigger outcome sync to Moodle.
2. Verify score and skills payload in LMS view.

Expected:
- Payload includes skills_mastered and skills_needing_support.
- Retry logic handles transient failures.

## 8) Script G: MIS and Certification

Steps:
1. Open MIS dashboard and export report.
2. Publish result release.
3. Issue and verify certificate.

Expected:
- Dashboards show tenant-scoped data.
- Certificate verification endpoint returns valid status.

## 9) Script H: Simulator-Driven Demo

Steps:
1. Run quick demo scenario.
2. Validate generated tenant, batch, learners, submissions.
3. Purge scenario.

Expected:
- All synthetic records carry scenario_id.
- Purge removes scenario artifacts.

## 10) UAT Exit Criteria

- 100 percent critical scripts passed.
- No Sev1 defects open.
- Pressure-point gates green for release window.
