from typing import Any

from pydantic import BaseModel, Field


class LearningModuleRequest(BaseModel):
    topic: str = Field(min_length=3)
    level: str = Field(default="beginner")
    goals: list[str] = Field(default_factory=list)


class LearningModuleResponse(BaseModel):
    roadmap: list[str]
    quiz: list[dict[str, Any]]
    summary: str


class EvaluateSubmissionRequest(BaseModel):
    assignment_id: str
    learner_id: str
    language: str = "python"
    repo_url: str
    commit_hash: str
    tests_path: str = "tests"


class EvaluateSubmissionResponse(BaseModel):
    assignment_id: str
    learner_id: str
    score: float
    test_pass_rate: float
    execution_ms: int
    memory_mb: int
    ai_feedback: str
    plagiarism_risk: str


class MoodleSyncRequest(BaseModel):
    learner_id: str
    assignment_id: str
    score: float
    feedback: str


class SimulatorScenarioRequest(BaseModel):
    scenario: dict[str, Any]


class SimulatorTemplateCreateRequest(BaseModel):
    tenant_id: str
    scenario_id: str
    connector_type: str = "moodle"


class SimulatorConnectorConfigureRequest(BaseModel):
    connector: dict[str, Any]


class SimulatorScenarioStatus(BaseModel):
    status: str
    scenarioId: str


class SimulatorRunResponse(BaseModel):
    status: str
    report: dict[str, Any]


class SimulatorScenarioStateResponse(BaseModel):
    scenario_id: str
    status: str
    created_at: str
    updated_at: str
    run_count: int
    last_report: dict[str, Any]


class MoodleCatalogueLookupRequest(BaseModel):
    query: str | None = None
    include_sections: bool = False
    limit: int = Field(default=20, ge=1, le=100)


class MoodleUserLookupRequest(BaseModel):
    query: str
    limit: int = Field(default=20, ge=1, le=100)


class MoodleActivityPlanItem(BaseModel):
    title: str = Field(min_length=3)
    activity_type: str = Field(
        default="assignment",
        pattern="^(assignment|practice|project|assessment)$",
    )
    delivery_mode: str = Field(default="individual", pattern="^(individual|group)$")
    week: int | None = Field(default=None, ge=1, le=52)
    day: int | None = Field(default=None, ge=1, le=7)
    topic: str | None = None
    section_name: str | None = None
    instructions: str = ""
    due_at_unix: int | None = None


class MoodleCourseProvisionRequest(BaseModel):
    course_id: int
    activities: list[MoodleActivityPlanItem]
    user_ids: list[int] = Field(default_factory=list)
    role_id: int = 5
    dry_run: bool = True


class MoodleCohortLookupRequest(BaseModel):
    query: str | None = None
    limit: int = Field(default=20, ge=1, le=100)


class MoodleCohortCourseSyncRequest(BaseModel):
    cohort_id: int
    course_id: int
    role_id: int = 5
    dry_run: bool = True


class MoodleConnectorPublishRequest(BaseModel):
    course_id: int
    activities: list[MoodleActivityPlanItem] = Field(default_factory=list)
    user_ids: list[int] = Field(default_factory=list)
    cohort_id: int | None = None
    role_id: int = 5
    dry_run: bool = True
    stop_on_error: bool = True


class TenantCreateRequest(BaseModel):
    tenant_id: str = Field(min_length=3)
    name: str = Field(min_length=2)
    quotas: dict[str, int] = Field(default_factory=dict)


class TenantUserRolesRequest(BaseModel):
    roles: list[str] = Field(default_factory=list)


class TenantImpersonationRequest(BaseModel):
    tenant_id: str = Field(min_length=3)
    assumed_roles: list[str] = Field(default_factory=list)


class ContextBridgeGenerateRequest(BaseModel):
    tenant_id: str = Field(min_length=3)
    source_type: str = Field(pattern="^(url|readme)$")
    source: str = Field(min_length=3)
    title_hint: str | None = None
    level: str = "intermediate"


class EvidenceEvent(BaseModel):
    ts: int = Field(ge=0)
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)


class EvidenceSessionIngestRequest(BaseModel):
    tenant_id: str = Field(min_length=3)
    learner_id: str = Field(min_length=2)
    assignment_id: str = Field(min_length=2)
    persona: str | None = None
    events: list[EvidenceEvent] = Field(default_factory=list)


class CompetencyItem(BaseModel):
    code: str
    score: float = Field(ge=0, le=100)
    evidence_session_id: str | None = None


class HandoverToLmsRequest(BaseModel):
    tenant_id: str = Field(min_length=3)
    learner_id: str = Field(min_length=2)
    assignment_id: str = Field(min_length=2)
    lms_return_url: str = Field(min_length=4)
    competencies: list[CompetencyItem] = Field(default_factory=list)


class GhostPersonaRunRequest(BaseModel):
    tenant_id: str = Field(min_length=3)
    assignment_id: str = Field(min_length=2)
    learner_id: str = Field(min_length=2)
    persona: str = Field(pattern="^(expert|struggler|cheater)$")
