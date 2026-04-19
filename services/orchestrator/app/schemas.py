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
