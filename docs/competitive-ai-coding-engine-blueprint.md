# Final Blueprint: AI-Powered Coding Practice and Assessment Platform

## 1) Executive Summary

This is a connector-first, generative-first platform design for coding practice and assessment.

- Today: Moodle is the active LMS integration.
- Future: any customer LMS or partner LMS connects through configurable tenant-level connectors.
- Core value: keep LMS as the planning hub and use the coding platform as the execution and intelligence engine.

The platform differentiates through a clear triangle:
- Zero-Shot Authoring: create learning and assessment tracks from one source URL.
- Binary-Plus Scoring: 70% deterministic baseline + 30% AI insight.
- Active Shadowing: in-editor, near real-time AI coaching with strict latency targets.

## 2) Operating Model (Hub-Spoke)

### Hub (LMS)
- Identity source of record (roster, enrollment, role context).
- Curriculum planning (courses, portions, calendar intent).
- Institutional tracking (completion, gradebook, competency map).

### Spoke (Coding Platform)
- Monaco-based coding workspace and conversational scaffolding.
- Process-aware evaluation (edit trace, dialogue progression, code evidence).
- Deterministic execution, AI insight generation, integrity analytics.

### Closed loop
1. Learner starts in LMS.
2. LTI 1.3 launch transfers identity and curriculum context.
3. Learner works in coding workspace with active shadowing.
4. Submission is evaluated with Binary-Plus scoring.
5. Competency-rich payload is synced back to LMS.

## 3) System Principles

- Configurable connector architecture, not LMS-specific custom code.
- No mock data in product services (dev, staging, prod).
- Separate Simulation Service for all demo and synthetic data needs.
- Deterministic-first trust model for high-stakes scenarios.
- Tenant-safe design from day one (claims, policy, data partitioning).
- Low-latency interaction as a product requirement.

## 4) Connector-First Architecture

## 4.1 Connector Contract (tenant configurable)
Each connector must support:
- Launch and SSO: LTI 1.3 or equivalent.
- Identity mapping: learner, instructor, evaluator roles.
- Curriculum context mapping: course, module, portion, calendar window.
- Outcome sync: score, competency tags, evidence references.
- Webhook/events: enrollment, assignment state, result publication.
- Health checks: connectivity, auth, schema compatibility.

## 4.2 Connector Lifecycle
1. Super admin enables connector type.
2. Tenant admin configures endpoints, credentials, role mappings.
3. Validation suite runs contract tests.
4. Connector becomes active for tenant onboarding and runtime sync.

## 4.3 Moodle now, partner LMS later
- Moodle is the reference connector and onboarding baseline.
- Connector abstraction is reused for future LMS partners.
- New LMS integrations are adapter implementations of the same contract.

## 5) Frontend Product Architecture

Frontend is workflow-driven with role-specific cockpits.

### 5.1 Frontend apps
- Super Admin Console
- Tenant Admin Portal
- Assessment Studio (Instructor/Author)
- Candidate Workspace
- Evaluator and Insights Console
- MIS and Reporting Portal
- Results and Certification Portal

### 5.2 Shared shell capabilities
- SSO and role switch
- Tenant switch
- Notifications
- Global search
- Audit-aware activity feed
- Feature flags and entitlements

### 5.3 Candidate workspace requirements (VS Code-like)
- Monaco editor with activity bar, explorer, tabs, problems panel, source control panel.
- Keyboard-first flow: command palette, quick open, run tests, diagnostics navigation.
- Git loop built-in: stage, commit, diff, submit.
- Active shadowing as non-blocking inline cues.
- Explain-why checkpoints for process evidence.
- Session continuity: autosave and restore.

## 6) Multi-Tenancy and Access Model

### 6.1 Tenant isolation
- Phase 1: strict logical isolation with tenant claims and guarded queries.
- Phase 3 option: physical isolation for premium enterprise tenants.

### 6.2 Required claims on secured requests
- tenant_id
- org_id
- actor_id
- role
- mode (practice/interview/exam when relevant)

### 6.3 Role lifecycle
1. Super admin provisions tenant.
2. Tenant admin configures identity, branding, policies.
3. Instructor publishes tracks and assigns batches.
4. Candidate accesses workspace by batch and mode.
5. Evaluator reviews evidence and decides outcomes.
6. MIS consumes analytics and exports.
7. Results manager releases outcomes and certificates.

## 7) Scoring and Integrity

### 7.1 Binary-Plus model
- Baseline (70%): deterministic correctness from tests.
- Plus (30%): AI insight from reasoning, pattern choice, explanation quality.

Formula:
S = 0.7B + 0.3P

### 7.2 Process-over-product integrity
- Edit trace behavior
- Dialogue progression quality
- Code evolution pattern
- Anomaly and plagiarism indicators

High-stakes mode:
- Deterministic components dominate.
- Assistance caps and fade-out enforced.
- Full audit replay retained.

## 8) Model and Latency Strategy

### 8.1 Tiered inference
- Tier 1 real-time intervention: fast local model (for example Qwen2.5-Coder 7B).
- Tier 2 post-submission deep critique: larger reasoning models.
- Tier 3 cohort analytics and drift checks: async batch jobs.

### 8.2 Latency goals
- Real-time intervention p50 below 2 seconds.
- Real-time intervention p95 by agreed SLA threshold.
- Deeper post-submission insight can be slower and asynchronous.

## 9) Competency-Rich LMS Sync

Outcome payload to LMS should include:
- overall_score
- baseline_score
- insight_score
- skills_mastered
- skills_needing_support
- evidence_refs (test ids, code spans, dialogue checkpoints)
- integrity_flags (if any)

This enables adaptive learning paths and mastery tracking, not score-only reporting.

## 10) Simulation Service (separate app)

## 10.1 Why separate
- Prevent mock logic from polluting product runtime.
- Ensure reproducible demos and QA runs.
- Support historical replay and analytics population.

## 10.2 Simulator capabilities
- One-click demo tenant bootstrap.
- Course and batch generation with pedagogy and calendar.
- Learner/evaluator persona generation.
- Attempt and submission simulation.
- Evaluation and LMS sync triggering.
- Replay historical batches.
- Purge/reset by scenario and tenant.

## 10.3 Simulator constraints
- Writes only via approved APIs/connectors.
- All records tagged with simulation_source and scenario_id.
- Deterministic seed support for repeatable runs.

## 10.4 Initial scenario packs
- Quick demo pack
- Academic cohort pack
- Hiring assessment pack
- Integrity stress pack
- Latency load pack
- Historical replay pack

## 11) Screen-to-API Readiness Checklist

### Super admin
- Tenant lifecycle APIs
- Global policy and model routing APIs
- Platform audit and health APIs

### Tenant admin
- Org setup APIs
- User and role APIs
- Batch and integration setup APIs

### Instructor
- Zero-shot generation APIs
- Track publish APIs
- Competency and hint policy APIs

### Candidate
- Attempt bootstrap APIs
- Workspace event APIs
- Realtime intervention APIs
- Submission and result APIs

### Evaluator
- Review queue APIs
- Evidence packet APIs
- Decision and override APIs

### MIS and certification
- Analytics APIs
- Export APIs
- Result release and certificate APIs

### Quality gates
- No screen depends on hardcoded mock payloads.
- Tenant and role claims validated end to end.
- Evidence IDs are stable and replayable.

## 12) Phased Delivery Plan

## Phase 0 (Weeks 1-3): Foundation freeze
- Finalize connector contract and Moodle reference mapping.
- Freeze route map, role matrix, and permission model.
- Define no-mock-data policy and Simulator Service spec.
- Finalize Binary-Plus scoring and competency payload schema.

Deliverables:
- Approved architecture and contracts.
- API schema set with claims and tenancy guards.
- Simulator scenario schema and tagging standards.

## Phase 1 (Weeks 4-10): MVP execution path
- Candidate workspace MVP with active shadowing.
- Moodle connector onboarding flow for tenant setup.
- Instructor zero-shot creation and publish workflow.
- Evaluator basic review and decision workflow.
- Simulator MVP for demo tenant and new batch setup.

Acceptance gates:
- Real-time intervention p50 below 2 seconds.
- First-task completion median below 5 minutes.
- Tenant to first active batch median below 30 minutes.
- No mock data in product services.

## Phase 2 (Weeks 11-18): Feature parity and scale prep
- Expand language runners.
- Hint fade-out engine by mode.
- MIS dashboards and scheduled exports.
- Results release and certification workflow.
- Historical replay scenarios in simulator.

## 13) Practical Moodle Connector Implementation (Now)

The orchestrator now exposes connector endpoints that support real Moodle Web Service integration patterns (with dry-run support before writing anything):

- POST /connectors/moodle/catalogue/lookup
- POST /connectors/moodle/users/lookup
- POST /connectors/moodle/courses/provision
- POST /connectors/moodle/cohorts/lookup
- POST /connectors/moodle/cohorts/sync-course
- POST /connectors/moodle/publish

### 13.1 What this enables

- Lookup catalog courses by search term and optionally include sections/topics.
- Lookup users for manual enrollment.
- Provision course activities aligned to selected course sections with week/day/topic context.
- Activity types accepted by planning model:
  - assignment
  - practice
  - project
  - assessment
- Delivery mode options:
  - individual
  - group

### 13.2 Provision flow

1. Select a Moodle course from catalogue lookup.
2. Build an activity plan with title, type, delivery mode, and scheduling context (week/day/topic/section_name).
3. Call provision endpoint with dry_run=true first to validate section placement and intended changes.
4. Re-submit with dry_run=false to create sections (if needed), create activities, and optionally enroll users.
5. Optionally sync cohort members to the same course using cohort sync endpoint.
6. For operational simplicity, use single publish endpoint to run provisioning + cohort sync with step-level status in one call.

### 13.3 Recommended data model for course structure alignment

For production rollout, represent curriculum intent in the platform with explicit hierarchy:

- Catalog
- Cohort
- Course
- Section/Topic
- Activity (assignment/practice/project/assessment)

Each activity should carry:

- course_id
- section_name or week
- day
- topic
- activity_type
- delivery_mode
- due_at
- connector_metadata (external ids returned by Moodle)

### 13.4 Recommendation for real implementation at scale

- Keep connector operations command-based and idempotent:
  - upsert course structures
  - upsert activities
  - upsert enrollments
- Store connector operation logs with request_id, actor_id, tenant_id, and external Moodle ids.
- Enforce two-step publish:
  - Draft (dry-run preview)
  - Commit (write to Moodle)
- Add reconciliation job:
  - compare platform intent vs Moodle actual state
  - detect drift and propose repair
- Add capability discovery per tenant connector (enabled wsfunctions) and degrade gracefully when a function is unavailable.

### 13.5 Catalogue/Cohort/Course lookup strategy

Recommended production lookup path:

1. Catalogue lookup returns eligible courses for tenant context.
2. Cohort lookup returns eligible learner groups for that tenant/program.
3. Course selection drives section/topic discovery.
4. Activity planning binds to section + week/day/topic.
5. Cohort sync binds selected cohort members to selected course and role.

This sequence keeps planning semantics clear for instructors while preserving deterministic connector operations and replayable audit trails.

Acceptance gates:
- Full role journey passes end-to-end validation.
- Competency payload powers adaptive sequencing in LMS.
- Evaluator throughput and fairness metrics visible.

## Phase 3 (Weeks 19-28): Enterprise hardening
- Multi-tenant enterprise controls.
- Enhanced observability and SLA management.
- Optional physical tenant isolation.
- Compliance and audit export readiness.

Acceptance gates:
- SLA stability under load tests.
- Audit replay for complete candidate journey.
- Connector certification process for partner LMS adapters.

## 13) 60-Day Milestone Board

- Days 1-7: Contracts and guardrails freeze.
- Days 8-21: Shared shell, tenant lifecycle, onboarding.
- Days 22-35: Candidate workspace, interventions, submissions.
- Days 36-49: Instructor, evaluator, competency sync.
- Days 50-60: MIS, certificates, simulator rollout and replay.

Day-60 launch gate:
- Measured latency goals met.
- End-to-end demo journey reproducible via simulator.
- Connector health checks green for onboarding path.
- No product service mock dataset usage detected.

## 14) KPIs

Product and UX:
- First-task completion time
- Intervention response latency (p50, p95)
- Hint acceptance and fade-out effectiveness

Learning and quality:
- Competency mastery progression
- Remediation success rate
- Correlation with evaluator outcomes

Operations and reliability:
- Job success rate
- Queue and connector health
- Tenant onboarding lead time

Integrity and governance:
- Confirmed anomaly precision
- Override rates and rationale quality
- Audit completeness

## 15) Key Risks and Mitigations

- Over-assistance dependency:
  - Mitigation: hint budgets and fade-out controls.
- Latency regressions from oversized models:
  - Mitigation: strict tiered inference routing.
- Connector drift across LMS vendors:
  - Mitigation: certification suite and contract tests.
- Multi-tenant leakage risk:
  - Mitigation: claims enforcement, partition guards, audit alerts.
- Analytics quality without real usage:
  - Mitigation: simulator replay and labeled synthetic cohorts.

## 16) Final Implementation Decisions to Lock

1. Connector contract version 1 and Moodle reference adapter scope.
2. Tenant isolation baseline and enterprise upgrade path.
3. Binary-Plus scoring schema and high-stakes policy mode.
4. Competency payload fields and LMS mapping rules.
5. Real-time model tier and latency SLO.
6. Simulation Service ownership, access policy, and purge governance.
7. Frontend app boundary strategy: unified shell with role modules.

## 17) Final Plan Statement

Build a connector-first, simulator-backed, multi-tenant coding platform where LMS remains the planning hub and the coding engine is the execution and intelligence spoke. Deliver Phase 1 with Moodle as the reference connector, enforce no mock data in product runtime, validate all journeys through the Simulator Service, and scale to partner LMS integrations through the same configurable connector contract.
