from fastapi.testclient import TestClient

from app.main import app


def test_moodle_catalogue_lookup(monkeypatch) -> None:
    async def fake_lookup_courses(query: str | None, limit: int):
        assert query == "physics"
        assert limit == 10
        return [{"id": 11, "shortname": "PHY101", "fullname": "Physics 101"}]

    async def fake_sections(course_id: int):
        assert course_id == 11
        return [{"id": 7, "section": 1, "name": "Week 1: Motion", "visible": 1}]

    monkeypatch.setattr("app.routers.connectors.moodle_lookup_courses", fake_lookup_courses)
    monkeypatch.setattr("app.routers.connectors.moodle_get_course_sections", fake_sections)

    client = TestClient(app)
    response = client.post(
        "/connectors/moodle/catalogue/lookup",
        json={"query": "physics", "limit": 10, "include_sections": True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["items"][0]["id"] == 11
    assert payload["items"][0]["sections"][0]["name"] == "Week 1: Motion"


def test_moodle_users_lookup(monkeypatch) -> None:
    async def fake_lookup_users(query: str, limit: int):
        assert query == "alice"
        assert limit == 5
        return [{"id": 42, "username": "alice", "fullname": "Alice Chen"}]

    monkeypatch.setattr("app.routers.connectors.moodle_lookup_users", fake_lookup_users)

    client = TestClient(app)
    response = client.post(
        "/connectors/moodle/users/lookup",
        json={"query": "alice", "limit": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["items"][0]["id"] == 42


def test_moodle_course_provision_dry_run(monkeypatch) -> None:
    async def fake_provision(**kwargs):
        assert kwargs["course_id"] == 11
        assert kwargs["dry_run"] is True
        assert len(kwargs["activities"]) == 2
        return {
            "course_id": 11,
            "dry_run": True,
            "planned": [
                {
                    "title": "Week 1 Practice",
                    "activity_type": "practice",
                    "delivery_mode": "individual",
                    "section_name": "Week 1: Basics",
                    "section_number": 1,
                    "will_create_section": False,
                }
            ],
            "created_sections": [],
            "created_activities": [],
            "enrolment": {"status": "planned", "count": 1},
        }

    monkeypatch.setattr(
        "app.routers.connectors.moodle_provision_course_activities",
        fake_provision,
    )

    client = TestClient(app)
    response = client.post(
        "/connectors/moodle/courses/provision",
        json={
            "course_id": 11,
            "dry_run": True,
            "user_ids": [42],
            "activities": [
                {
                    "title": "Week 1 Practice",
                    "activity_type": "practice",
                    "delivery_mode": "individual",
                    "week": 1,
                    "topic": "Basics",
                    "instructions": "Solve exercises 1-5",
                },
                {
                    "title": "Week 2 Group Project",
                    "activity_type": "project",
                    "delivery_mode": "group",
                    "week": 2,
                    "topic": "Applications",
                    "instructions": "Submit as group",
                },
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["dry_run"] is True
    assert payload["course_id"] == 11


def test_moodle_cohort_lookup(monkeypatch) -> None:
    async def fake_lookup_cohorts(query: str | None, limit: int):
        assert query == "batch a"
        assert limit == 10
        return [{"id": 9, "name": "Batch A", "idnumber": "BATCH_A"}]

    monkeypatch.setattr("app.routers.connectors.moodle_lookup_cohorts", fake_lookup_cohorts)

    client = TestClient(app)
    response = client.post(
        "/connectors/moodle/cohorts/lookup",
        json={"query": "batch a", "limit": 10},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["items"][0]["id"] == 9


def test_moodle_cohort_course_sync_dry_run(monkeypatch) -> None:
    async def fake_sync(**kwargs):
        assert kwargs["cohort_id"] == 9
        assert kwargs["course_id"] == 11
        assert kwargs["dry_run"] is True
        return {
            "cohort_id": 9,
            "course_id": 11,
            "dry_run": True,
            "member_count": 3,
            "planned_enrolments": 3,
            "member_user_ids": [41, 42, 43],
        }

    monkeypatch.setattr("app.routers.connectors.moodle_sync_cohort_to_course", fake_sync)

    client = TestClient(app)
    response = client.post(
        "/connectors/moodle/cohorts/sync-course",
        json={"cohort_id": 9, "course_id": 11, "role_id": 5, "dry_run": True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["cohort_id"] == 9
    assert payload["course_id"] == 11
    assert payload["planned_enrolments"] == 3


def test_moodle_publish_success(monkeypatch) -> None:
    async def fake_provision(**kwargs):
        assert kwargs["course_id"] == 11
        return {"course_id": 11, "dry_run": True, "planned": []}

    async def fake_sync(**kwargs):
        assert kwargs["cohort_id"] == 9
        return {"cohort_id": 9, "course_id": 11, "dry_run": True, "planned_enrolments": 2}

    monkeypatch.setattr("app.routers.connectors.moodle_provision_course_activities", fake_provision)
    monkeypatch.setattr("app.routers.connectors.moodle_sync_cohort_to_course", fake_sync)

    client = TestClient(app)
    response = client.post(
        "/connectors/moodle/publish",
        json={
            "course_id": 11,
            "cohort_id": 9,
            "dry_run": True,
            "activities": [
                {
                    "title": "Week 1 Assessment",
                    "activity_type": "assessment",
                    "delivery_mode": "individual",
                    "week": 1,
                    "topic": "Foundations",
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert len(payload["steps"]) == 2
    assert payload["steps"][0]["name"] == "course_provision"
    assert payload["steps"][1]["name"] == "cohort_sync"


def test_moodle_publish_stop_on_error(monkeypatch) -> None:
    async def failing_provision(**kwargs):
        raise RuntimeError("provision failed")

    async def fake_sync(**kwargs):
        raise AssertionError("cohort sync should not run when stop_on_error is true")

    monkeypatch.setattr("app.routers.connectors.moodle_provision_course_activities", failing_provision)
    monkeypatch.setattr("app.routers.connectors.moodle_sync_cohort_to_course", fake_sync)

    client = TestClient(app)
    response = client.post(
        "/connectors/moodle/publish",
        json={
            "course_id": 11,
            "cohort_id": 9,
            "dry_run": True,
            "stop_on_error": True,
            "activities": [
                {
                    "title": "Week 1 Practice",
                    "activity_type": "practice",
                    "delivery_mode": "individual",
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "failed"
    assert len(payload["steps"]) == 1
    assert payload["steps"][0]["name"] == "course_provision"
    assert payload["steps"][0]["status"] == "failed"


def test_moodle_publish_writes_history_and_can_be_queried(monkeypatch) -> None:
    records: list[dict] = []

    async def fake_provision(**kwargs):
        return {"course_id": kwargs["course_id"], "dry_run": True, "planned": []}

    def fake_append(record: dict):
        records.append(record)

    def fake_list(
        limit: int,
        tenant_id: str | None,
        course_id: int | None,
        status: str | None,
    ):
        rows = records
        if tenant_id is not None:
            rows = [row for row in rows if row.get("tenant_id") == tenant_id]
        if course_id is not None:
            rows = [row for row in rows if row.get("course_id") == course_id]
        if status is not None:
            rows = [row for row in rows if row.get("status") == status]
        return rows[:limit]

    def fake_get(request_id: str):
        for row in records:
            if row.get("request_id") == request_id:
                return row
        return None

    monkeypatch.setattr("app.routers.connectors.moodle_provision_course_activities", fake_provision)
    monkeypatch.setattr("app.routers.connectors.append_publish_history", fake_append)
    monkeypatch.setattr("app.routers.connectors.list_publish_history", fake_list)
    monkeypatch.setattr("app.routers.connectors.get_publish_history_record", fake_get)

    client = TestClient(app)
    publish_response = client.post(
        "/connectors/moodle/publish",
        json={
            "course_id": 21,
            "dry_run": True,
            "activities": [
                {
                    "title": "Week 3 Practice",
                    "activity_type": "practice",
                    "delivery_mode": "individual",
                }
            ],
        },
    )

    assert publish_response.status_code == 200
    published = publish_response.json()
    assert published["request_id"]

    list_response = client.get("/connectors/moodle/publish/history?course_id=21")
    assert list_response.status_code == 200
    listed = list_response.json()
    assert listed["count"] == 1

    request_id = listed["items"][0]["request_id"]
    get_response = client.get(f"/connectors/moodle/publish/history/{request_id}")
    assert get_response.status_code == 200
    assert get_response.json()["course_id"] == 21


def test_moodle_publish_history_by_id_not_found(monkeypatch) -> None:
    def fake_get(_request_id: str):
        return None

    monkeypatch.setattr("app.routers.connectors.get_publish_history_record", fake_get)

    client = TestClient(app)
    response = client.get("/connectors/moodle/publish/history/does-not-exist")

    assert response.status_code == 404
