from fastapi.testclient import TestClient

from app.main import app


def _payload() -> dict[str, str]:
    return {
        "assignment_id": "a1",
        "learner_id": "u1",
        "language": "python",
        "repo_url": "https://example.com/repo.git",
        "commit_hash": "abc123",
        "tests_path": "tests",
    }


def _runner_result() -> dict[str, float | int]:
    return {
        "test_pass_rate": 0.9,
        "execution_ms": 750,
        "memory_mb": 120,
    }


def test_assessment_mode_deterministic(monkeypatch) -> None:
    async def fake_run_assessment(_: dict):
        return _runner_result()

    async def fake_generate_with_ollama(*args, **kwargs):
        raise AssertionError("LLM should not be called in deterministic mode")

    async def fake_sync_to_moodle(_: dict):
        return {"status": "queued"}

    monkeypatch.setattr("app.routers.assessment.run_assessment", fake_run_assessment)
    monkeypatch.setattr("app.routers.assessment.generate_with_ollama", fake_generate_with_ollama)
    monkeypatch.setattr("app.routers.assessment.sync_to_moodle", fake_sync_to_moodle)

    client = TestClient(app)
    response = client.post("/assessment/evaluate?mode=deterministic", json=_payload())

    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 90.0
    assert "Cache repeated computations where possible." in data["ai_feedback"]


def test_assessment_mode_llm(monkeypatch) -> None:
    async def fake_run_assessment(_: dict):
        return _runner_result()

    async def fake_generate_with_ollama(*args, **kwargs):
        return "LLM feedback line 1\nLLM feedback line 2\nLLM feedback line 3"

    async def fake_sync_to_moodle(_: dict):
        return {"status": "queued"}

    monkeypatch.setattr("app.routers.assessment.run_assessment", fake_run_assessment)
    monkeypatch.setattr("app.routers.assessment.generate_with_ollama", fake_generate_with_ollama)
    monkeypatch.setattr("app.routers.assessment.sync_to_moodle", fake_sync_to_moodle)

    client = TestClient(app)
    response = client.post("/assessment/evaluate?mode=llm", json=_payload())

    assert response.status_code == 200
    data = response.json()
    assert data["ai_feedback"].startswith("LLM feedback line 1")


def test_assessment_mode_auto_respects_settings(monkeypatch) -> None:
    async def fake_run_assessment(_: dict):
        return _runner_result()

    async def fake_generate_with_ollama(*args, **kwargs):
        return "AUTO LLM feedback"

    async def fake_sync_to_moodle(_: dict):
        return {"status": "queued"}

    monkeypatch.setattr("app.routers.assessment.run_assessment", fake_run_assessment)
    monkeypatch.setattr("app.routers.assessment.generate_with_ollama", fake_generate_with_ollama)
    monkeypatch.setattr("app.routers.assessment.sync_to_moodle", fake_sync_to_moodle)
    monkeypatch.setattr("app.routers.assessment.settings.assessment_use_ollama", True)

    client = TestClient(app)
    response = client.post("/assessment/evaluate?mode=auto", json=_payload())

    assert response.status_code == 200
    assert response.json()["ai_feedback"] == "AUTO LLM feedback"


def test_assessment_mode_rejects_invalid_mode() -> None:
    client = TestClient(app)
    response = client.post("/assessment/evaluate?mode=invalid", json=_payload())

    assert response.status_code == 422
