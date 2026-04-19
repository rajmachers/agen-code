# Frontend IA and Navigation Specification

## 1) Purpose

Define role-based information architecture, navigation hierarchy, and UX acceptance standards for all frontend apps.

## 2) Global Shell

Global navigation elements:
- tenant switcher
- role switcher
- notifications
- global search
- profile and session controls

Global states:
- loading
- empty
- no-permission
- connector-unavailable
- degraded-mode

## 3) Role-Based IA

## Super Admin
Primary sections:
- platform home
- tenants
- policy packs
- model routing
- compliance and audit
- platform insights

## Tenant Admin
Primary sections:
- tenant home
- organization setup
- users and roles
- batch management
- integrations
- security and retention

## Instructor
Primary sections:
- studio home
- zero-shot generation
- track review and publish
- competencies
- hint policy
- learner monitoring

## Candidate
Primary sections:
- dashboard
- batches and assessments
- workspace
- submissions and feedback
- results and certificates

## Evaluator
Primary sections:
- review queue
- deep review
- replay
- decisions
- fairness panel

## MIS
Primary sections:
- executive summary
- cohort analytics
- skill heatmaps
- operations
- exports

## Certification Manager
Primary sections:
- release control
- certificate issuance
- verification
- transcript management

## 4) Candidate Workspace Layout

Panels:
- left: explorer and source control
- center: editor tabs
- right: intervention stream and intent chat
- bottom: terminal and test output

Workflow actions:
- run checks
- request hint
- explain approach
- stage and commit
- submit snapshot

## 5) Navigation Rules

- no direct route access without role guard validation
- mode-sensitive actions (practice, interview, exam)
- exam mode suppresses non-permitted assist actions
- every decision action has confirm and audit marker

## 6) UX Acceptance Criteria

- keyboard-first navigation works for core paths
- no critical action hidden behind non-obvious controls
- all error states include recovery guidance
- first-time candidate reaches workspace and submits in target time window
- intervention UI remains non-blocking under latency fallback mode

## 7) Accessibility Baseline

- clear focus states
- semantic landmarks
- contrast compliance in key flows
- screen-reader labels for critical controls

## 8) Telemetry Hooks

Track events:
- route enter and exit
- feature action use
- intervention request and response timings
- hint acceptance and rejection
- submission completion steps

Telemetry must include:
- tenant_id
- role
- mode
- request_id
