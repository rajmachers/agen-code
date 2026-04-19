import app.main as simulator_main
from fastapi.testclient import TestClient


def _valid_connector_payload(tenant_id: str = "tenant_01") -> dict:
    return {
        "tenantId": tenant_id,
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


def _valid_scenario_payload(scenario_id: str = "demo_001") -> dict:
    return {
        "scenarioId": scenario_id,
        "scenarioType": "quick_demo",
        "seed": 12345,
        "tenantConfig": {"tenantId": "tenant_01", "connectorType": "moodle"},
        "courseConfig": {"courseCount": 2, "pedagogyProfile": "foundational"},
        "batchConfig": {
            "batchCount": 1,
            "modeMix": {"practice": 0.8, "interview": 0.1, "exam": 0.1},
        },
        "population": {"candidates": 40, "instructors": 2, "evaluators": 2},
        "timeline": {"mode": "accelerated", "durationDays": 14},
        "governance": {"simulationSource": "simulator_service", "purgeOnComplete": False},
    }


def _reset_db(tmp_path) -> None:
    simulator_main.DB_PATH = str(tmp_path / "simulator-test.db")
    simulator_main._init_db()
    with simulator_main._conn() as connection:
        connection.execute("DELETE FROM run_reports")
        connection.execute("DELETE FROM scenarios")
        connection.execute("DELETE FROM connectors")


def test_connector_crud_with_audit_metadata(tmp_path) -> None:
    _reset_db(tmp_path)
    client = TestClient(simulator_main.app)

    configure_response = client.post(
        "/sim/v1/connectors/configure",
        json={
            "payload": _valid_connector_payload(),
            "actor_id": "admin_01",
            "request_id": "req_001",
            "simulation_source": "simulator_service",
        },
    )
    assert configure_response.status_code == 200
    assert configure_response.json()["status"] == "configured"
    assert configure_response.json()["actor_id"] == "admin_01"
    assert configure_response.json()["request_id"] == "req_001"
    assert configure_response.json()["simulation_source"] == "simulator_service"

    list_response = client.get("/sim/v1/connectors")
    assert list_response.status_code == 200
    assert list_response.json()["count"] == 1
    item = list_response.json()["items"][0]
    assert item["tenantId"] == "tenant_01"
    assert item["actor_id"] == "admin_01"
    assert item["request_id"] == "req_001"
    assert item["simulation_source"] == "simulator_service"

    get_response = client.get("/sim/v1/connectors/tenant_01")
    assert get_response.status_code == 200
    assert get_response.json()["payload"]["tenantId"] == "tenant_01"
    assert get_response.json()["actor_id"] == "admin_01"
    assert get_response.json()["request_id"] == "req_001"
    assert get_response.json()["simulation_source"] == "simulator_service"

    delete_response = client.delete("/sim/v1/connectors/tenant_01")
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "deleted"

    missing_response = client.get("/sim/v1/connectors/tenant_01")
    assert missing_response.status_code == 404


def test_scenario_status_includes_audit_metadata(tmp_path) -> None:
    _reset_db(tmp_path)
    client = TestClient(simulator_main.app)

    create_response = client.post(
        "/sim/v1/scenarios/create",
        json={
            "payload": _valid_scenario_payload(),
            "actor_id": "author_01",
            "request_id": "req_010",
            "simulation_source": "simulator_service",
        },
    )
    assert create_response.status_code == 200
    assert create_response.json()["status"] == "created"
    assert create_response.json()["actor_id"] == "author_01"
    assert create_response.json()["request_id"] == "req_010"
    assert create_response.json()["simulation_source"] == "simulator_service"

    status_response = client.get("/sim/v1/scenarios/demo_001/status")
    assert status_response.status_code == 200
    assert status_response.json()["actor_id"] == "author_01"
    assert status_response.json()["request_id"] == "req_010"
    assert status_response.json()["simulation_source"] == "simulator_service"
