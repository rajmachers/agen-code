from fastapi.testclient import TestClient

from app.main import app


def test_simulator_create_and_status_routes(monkeypatch) -> None:
    async def fake_create(payload):
        return {"status": "created", "scenarioId": payload["scenarioId"]}

    async def fake_status(scenario_id):
        return {
            "scenario_id": scenario_id,
            "status": "created",
            "created_at": "2026-01-01T00:00:00+00:00",
            "updated_at": "2026-01-01T00:00:00+00:00",
            "run_count": 0,
            "last_report": {},
        }

    monkeypatch.setattr("app.routers.simulator.simulator_create_scenario", fake_create)
    monkeypatch.setattr("app.routers.simulator.simulator_get_status", fake_status)

    client = TestClient(app)

    create_response = client.post(
        "/simulator/scenarios",
        json={"scenario": {"scenarioId": "demo_001"}},
    )
    assert create_response.status_code == 200
    assert create_response.json() == {"status": "created", "scenarioId": "demo_001"}

    status_response = client.get("/simulator/scenarios/demo_001/status")
    assert status_response.status_code == 200
    assert status_response.json()["scenario_id"] == "demo_001"
    assert status_response.json()["status"] == "created"


def test_simulator_control_routes(monkeypatch) -> None:
    async def fake_run(scenario_id):
        return {"status": "run_completed", "report": {"scenarioId": scenario_id}}

    async def fake_replay(scenario_id):
        return {"status": "replay_completed", "report": {"scenarioId": scenario_id}}

    async def fake_pause(scenario_id):
        return {"status": "paused", "scenarioId": scenario_id}

    async def fake_resume(scenario_id):
        return {"status": "resumed", "scenarioId": scenario_id}

    monkeypatch.setattr("app.routers.simulator.simulator_run_scenario", fake_run)
    monkeypatch.setattr("app.routers.simulator.simulator_replay_scenario", fake_replay)
    monkeypatch.setattr("app.routers.simulator.simulator_pause_scenario", fake_pause)
    monkeypatch.setattr("app.routers.simulator.simulator_resume_scenario", fake_resume)

    client = TestClient(app)

    run_response = client.post("/simulator/scenarios/demo_001/run")
    assert run_response.status_code == 200
    assert run_response.json()["status"] == "run_completed"

    replay_response = client.post("/simulator/scenarios/demo_001/replay")
    assert replay_response.status_code == 200
    assert replay_response.json()["status"] == "replay_completed"

    pause_response = client.post("/simulator/scenarios/demo_001/pause")
    assert pause_response.status_code == 200
    assert pause_response.json() == {"status": "paused", "scenarioId": "demo_001"}

    resume_response = client.post("/simulator/scenarios/demo_001/resume")
    assert resume_response.status_code == 200
    assert resume_response.json() == {"status": "resumed", "scenarioId": "demo_001"}


def test_simulator_template_route(monkeypatch) -> None:
    async def fake_templates():
        return {"items": [{"templateId": "quick_demo"}], "count": 1}

    async def fake_create_from_template(template_id, tenant_id, scenario_id, connector_type):
        assert template_id == "quick_demo"
        assert tenant_id == "tenant_01"
        assert scenario_id == "scn_01"
        assert connector_type == "moodle"
        return {"status": "created", "scenarioId": scenario_id}

    monkeypatch.setattr("app.routers.simulator.simulator_list_templates", fake_templates)
    monkeypatch.setattr(
        "app.routers.simulator.simulator_create_from_template",
        fake_create_from_template,
    )

    client = TestClient(app)

    list_response = client.get("/simulator/scenarios/templates")
    assert list_response.status_code == 200
    assert list_response.json()["count"] == 1

    create_response = client.post(
        "/simulator/scenarios/templates/quick_demo",
        json={"tenant_id": "tenant_01", "scenario_id": "scn_01", "connector_type": "moodle"},
    )
    assert create_response.status_code == 200
    assert create_response.json() == {"status": "created", "scenarioId": "scn_01"}


def test_simulator_connector_configure_route(monkeypatch) -> None:
    async def fake_configure(payload):
        assert payload["tenantId"] == "tenant_01"
        return {
            "status": "configured",
            "tenantId": payload["tenantId"],
            "connectorType": payload["connectorType"],
        }

    monkeypatch.setattr("app.routers.simulator.simulator_configure_connector", fake_configure)

    client = TestClient(app)

    response = client.post(
        "/simulator/connectors/configure",
        json={
            "connector": {
                "tenantId": "tenant_01",
                "connectorType": "moodle",
                "contractVersion": "v1.0",
                "endpoints": {
                    "launchResolve": "https://example.org/launch",
                    "outcomePush": "https://example.org/outcome",
                    "health": "https://example.org/health",
                    "capabilities": "https://example.org/capabilities",
                },
                "auth": {
                    "method": "oauth2",
                    "clientId": "client_01",
                    "secretRef": "vault://secret",
                    "tokenUrl": "https://example.org/token",
                },
                "mappings": {
                    "roles": {
                        "instructor": "editingteacher",
                        "candidate": "student",
                        "evaluator": "noneditingteacher",
                    },
                    "course": "course_id",
                    "module": "module_id",
                    "activity": "activity_id",
                },
                "capabilities": {
                    "launch": True,
                    "rosterSync": True,
                    "competencySync": True,
                    "resultRelease": True,
                },
            }
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "configured"
    assert response.json()["tenantId"] == "tenant_01"
