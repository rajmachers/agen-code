from fastapi.testclient import TestClient

from app.main import app


def test_admin_tenant_and_role_management_flow() -> None:
    client = TestClient(app)

    create_tenant = client.post(
        "/admin/tenants",
        json={
            "tenant_id": "tenant_exec_1",
            "name": "Execution Tenant",
            "quotas": {"context_generations_daily": 3, "evidence_sessions_daily": 3, "handover_daily": 3},
        },
    )
    assert create_tenant.status_code == 200

    assign_roles = client.post(
        "/admin/tenants/tenant_exec_1/users/user_a/roles",
        json={"roles": ["tenant_admin", "teacher"]},
    )
    assert assign_roles.status_code == 200
    assert assign_roles.json()["roles"] == ["teacher", "tenant_admin"]

    list_users = client.get("/admin/tenants/tenant_exec_1/users")
    assert list_users.status_code == 200
    assert list_users.json()["count"] >= 1


def test_context_bridge_generate_review_and_approve(monkeypatch) -> None:
    client = TestClient(app)
    client.post(
        "/admin/tenants",
        json={"tenant_id": "tenant_exec_2", "name": "Authoring Tenant"},
    )

    response = client.post(
        "/authoring/context-bridge/generate",
        json={
            "tenant_id": "tenant_exec_2",
            "source_type": "readme",
            "source": "FastAPI microservice with JWT, RBAC, tenant isolation and Moodle sync.",
            "title_hint": "Zero Shot Track",
            "level": "intermediate",
        },
    )
    assert response.status_code == 200
    draft = response.json()
    draft_id = draft["draft_id"]
    assert draft["status"] == "draft"

    submit = client.post(f"/authoring/drafts/{draft_id}/submit-review")
    assert submit.status_code == 200
    assert submit.json()["status"] == "in_review"

    approve = client.post(f"/authoring/drafts/{draft_id}/approve")
    assert approve.status_code == 200
    assert approve.json()["status"] == "approved"


def test_evidence_replay_flags_cheater_pattern() -> None:
    client = TestClient(app)
    client.post(
        "/admin/tenants",
        json={"tenant_id": "tenant_exec_3", "name": "Evidence Tenant"},
    )

    ingest = client.post(
        "/evidence/sessions",
        json={
            "tenant_id": "tenant_exec_3",
            "learner_id": "learner_1",
            "assignment_id": "assign_1",
            "events": [
                {"ts": 1000, "event_type": "paste", "payload": {"chars": 150}},
                {"ts": 1400, "event_type": "paste", "payload": {"chars": 130}},
                {"ts": 1900, "event_type": "paste", "payload": {"chars": 140}},
            ],
        },
    )
    assert ingest.status_code == 200
    session_id = ingest.json()["session_id"]

    replay = client.get(f"/evidence/sessions/{session_id}/replay")
    assert replay.status_code == 200
    assert "copy_paste_heavy" in replay.json()["flags"]


def test_ghost_persona_run_and_lms_handover() -> None:
    client = TestClient(app)
    client.post(
        "/admin/tenants",
        json={"tenant_id": "tenant_exec_4", "name": "Ghost Tenant"},
    )

    ghost = client.post(
        "/simulator/personas/run",
        json={
            "tenant_id": "tenant_exec_4",
            "assignment_id": "assign_ghost",
            "learner_id": "learner_cheater",
            "persona": "cheater",
        },
    )
    assert ghost.status_code == 200
    session_id = ghost.json()["session_id"]
    assert "copy_paste_heavy" in ghost.json()["flags"]

    handover = client.post(
        "/delivery/handover/return-to-lms",
        json={
            "tenant_id": "tenant_exec_4",
            "learner_id": "learner_cheater",
            "assignment_id": "assign_ghost",
            "lms_return_url": "https://moodle.example/return",
            "competencies": [
                {"code": "algo.correctness", "score": 72.5, "evidence_session_id": session_id}
            ],
        },
    )
    assert handover.status_code == 200
    assert handover.json()["status"] == "ready_for_lms_return"
