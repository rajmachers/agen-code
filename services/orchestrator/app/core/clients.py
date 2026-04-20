from __future__ import annotations

import json
import time
from typing import Any

import httpx

from app.core.config import settings


def _flatten_moodle_params(prefix: str, value: Any, out: dict[str, str]) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            _flatten_moodle_params(f"{prefix}[{key}]", nested, out)
        return
    if isinstance(value, list):
        for idx, nested in enumerate(value):
            _flatten_moodle_params(f"{prefix}[{idx}]", nested, out)
        return
    out[prefix] = "" if value is None else str(value)


def _sanitize_section_name(candidate: str | None) -> str:
    base = (candidate or "").strip()
    return base if base else "General"


def _section_name_for_item(item: dict[str, Any]) -> str:
    explicit = _sanitize_section_name(item.get("section_name"))
    if explicit != "General":
        return explicit
    week = item.get("week")
    topic = (item.get("topic") or "").strip()
    if week and topic:
        return f"Week {week}: {topic}"
    if week:
        return f"Week {week}"
    if topic:
        return topic
    return "General"


def _assignment_description(item: dict[str, Any]) -> str:
    lines = [
        f"Type: {item.get('activity_type', 'assignment')}",
        f"Delivery: {item.get('delivery_mode', 'individual')}",
    ]
    if item.get("week"):
        lines.append(f"Week: {item['week']}")
    if item.get("day"):
        lines.append(f"Day: {item['day']}")
    if item.get("topic"):
        lines.append(f"Topic: {item['topic']}")
    if item.get("instructions"):
        lines.append("")
        lines.append(item["instructions"])
    return "\n".join(lines)


async def _moodle_ws_call(wsfunction: str, params: dict[str, Any] | None = None) -> Any:
    if not settings.moodle_token or settings.moodle_token == "replace-me":
        raise RuntimeError("MOODLE_TOKEN is not configured")

    endpoint = settings.moodle_base_url.rstrip("/") + "/webservice/rest/server.php"
    form: dict[str, str] = {
        "wstoken": settings.moodle_token,
        "wsfunction": wsfunction,
        "moodlewsrestformat": "json",
    }
    for key, value in (params or {}).items():
        _flatten_moodle_params(key, value, form)

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(endpoint, data=form)
        response.raise_for_status()
        payload = response.json()

    if isinstance(payload, dict) and payload.get("exception"):
        message = payload.get("message") or payload.get("errorcode") or "Moodle WS call failed"
        raise RuntimeError(f"{wsfunction}: {message}")
    return payload


async def moodle_lookup_courses(query: str | None, limit: int = 20) -> list[dict[str, Any]]:
    if query:
        payload = await _moodle_ws_call(
            "core_course_search_courses",
            {
                "criterianame": "search",
                "criteriavalue": query,
                "page": 0,
                "perpage": limit,
            },
        )
        courses = payload.get("courses", []) if isinstance(payload, dict) else []
        return [
            {
                "id": course.get("id"),
                "shortname": course.get("shortname"),
                "fullname": course.get("fullname"),
                "categoryid": course.get("categoryid"),
                "visible": course.get("visible"),
            }
            for course in courses
        ]

    payload = await _moodle_ws_call("core_course_get_courses")
    if not isinstance(payload, list):
        return []
    return [
        {
            "id": course.get("id"),
            "shortname": course.get("shortname"),
            "fullname": course.get("fullname"),
            "categoryid": course.get("categoryid"),
            "visible": course.get("visible"),
        }
        for course in payload[:limit]
    ]


async def moodle_get_course_sections(course_id: int) -> list[dict[str, Any]]:
    payload = await _moodle_ws_call("core_course_get_contents", {"courseid": course_id})
    if not isinstance(payload, list):
        return []
    return [
        {
            "id": section.get("id"),
            "section": section.get("section"),
            "name": section.get("name") or f"Section {section.get('section', 0)}",
            "visible": section.get("visible"),
        }
        for section in payload
    ]


async def moodle_lookup_users(query: str, limit: int = 20) -> list[dict[str, Any]]:
    payload = await _moodle_ws_call(
        "core_user_get_users",
        {
            "criteria": [{"key": "fullname", "value": query}],
        },
    )
    users = payload.get("users", []) if isinstance(payload, dict) else []
    return [
        {
            "id": user.get("id"),
            "username": user.get("username"),
            "fullname": user.get("fullname"),
            "email": user.get("email"),
        }
        for user in users[:limit]
    ]


async def moodle_lookup_cohorts(query: str | None, limit: int = 20) -> list[dict[str, Any]]:
    search = (query or "").strip()
    if not search:
        # Moodle rejects empty query for core_cohort_search_cohorts.
        return []
    payload = await _moodle_ws_call(
        "core_cohort_search_cohorts",
        {
            "query": search,
            "limitfrom": 0,
            "limitnum": limit,
        },
    )
    cohorts = payload.get("cohorts", []) if isinstance(payload, dict) else []
    return [
        {
            "id": cohort.get("id"),
            "name": cohort.get("name"),
            "idnumber": cohort.get("idnumber"),
            "contextid": cohort.get("contextid"),
            "visible": cohort.get("visible"),
        }
        for cohort in cohorts[:limit]
    ]


def _cohort_member_ids(payload: Any) -> list[int]:
    if isinstance(payload, dict):
        if isinstance(payload.get("userids"), list):
            return [int(user_id) for user_id in payload["userids"]]
        if isinstance(payload.get("users"), list):
            user_ids: list[int] = []
            for user in payload["users"]:
                if isinstance(user, dict) and user.get("id") is not None:
                    user_ids.append(int(user["id"]))
            return user_ids
        return []

    if isinstance(payload, list):
        ids: list[int] = []
        for item in payload:
            if isinstance(item, int):
                ids.append(int(item))
            elif isinstance(item, dict) and item.get("id") is not None:
                ids.append(int(item["id"]))
        return ids

    return []


async def moodle_sync_cohort_to_course(
    *,
    cohort_id: int,
    course_id: int,
    role_id: int,
    dry_run: bool,
) -> dict[str, Any]:
    members_payload = await _moodle_ws_call(
        "core_cohort_get_cohort_members",
        {"cohorttype": {"type": "id", "value": cohort_id}},
    )
    user_ids = _cohort_member_ids(members_payload)
    enrolments = [
        {
            "roleid": role_id,
            "userid": user_id,
            "courseid": course_id,
        }
        for user_id in user_ids
    ]

    if dry_run:
        return {
            "cohort_id": cohort_id,
            "course_id": course_id,
            "dry_run": True,
            "member_count": len(user_ids),
            "planned_enrolments": len(enrolments),
            "member_user_ids": user_ids,
        }

    if enrolments:
        await _moodle_ws_call("enrol_manual_enrol_users", {"enrolments": enrolments})

    return {
        "cohort_id": cohort_id,
        "course_id": course_id,
        "dry_run": False,
        "member_count": len(user_ids),
        "enrolled_count": len(enrolments),
    }


async def moodle_provision_course_activities(
    *,
    course_id: int,
    activities: list[dict[str, Any]],
    user_ids: list[int],
    role_id: int,
    dry_run: bool,
) -> dict[str, Any]:
    sections = await moodle_get_course_sections(course_id)
    by_name = {str(section["name"]).strip().lower(): section for section in sections}
    by_number = {int(section.get("section") or 0): section for section in sections}

    planned: list[dict[str, Any]] = []
    created_activities: list[dict[str, Any]] = []
    created_sections: list[dict[str, Any]] = []

    for item in activities:
        section_name = _section_name_for_item(item)
        target_section = by_name.get(section_name.lower())
        section_number = item.get("week") or None

        if target_section is None and section_number in by_number:
            target_section = by_number[section_number]

        if target_section is None and not dry_run:
            create_payload: dict[str, Any] = {
                "courseid": course_id,
                "sections": [{"name": section_name}],
            }
            if section_number:
                create_payload["sections"][0]["section"] = section_number
            created = await _moodle_ws_call("core_course_create_sections", create_payload)
            created_sections.append({
                "name": section_name,
                "response": created,
            })
            sections = await moodle_get_course_sections(course_id)
            by_name = {str(section["name"]).strip().lower(): section for section in sections}
            by_number = {int(section.get("section") or 0): section for section in sections}
            target_section = by_name.get(section_name.lower())
            if target_section is None and section_number in by_number:
                target_section = by_number[section_number]

        section_ref = int(target_section.get("section") or 0) if target_section else 0
        planned.append(
            {
                "title": item.get("title"),
                "activity_type": item.get("activity_type"),
                "delivery_mode": item.get("delivery_mode"),
                "section_name": section_name,
                "section_number": section_ref,
                "will_create_section": target_section is None,
            }
        )

        if dry_run:
            continue

        assignment = {
            "course": course_id,
            "name": item.get("title"),
            "intro": _assignment_description(item),
            "introformat": 1,
            "section": section_ref,
            "teamsubmission": 1 if item.get("delivery_mode") == "group" else 0,
        }
        due_at = item.get("due_at_unix")
        if due_at:
            assignment["duedate"] = int(due_at)

        response = await _moodle_ws_call("mod_assign_add_instance", {"assignment": assignment})
        created_activities.append(
            {
                "title": item.get("title"),
                "activity_type": item.get("activity_type"),
                "section_name": section_name,
                "response": response,
            }
        )

    enrolment_result: dict[str, Any] | None = None
    if user_ids:
        enrolments = [
            {
                "roleid": role_id,
                "userid": user_id,
                "courseid": course_id,
            }
            for user_id in user_ids
        ]
        if dry_run:
            enrolment_result = {"status": "planned", "count": len(enrolments)}
        else:
            await _moodle_ws_call("enrol_manual_enrol_users", {"enrolments": enrolments})
            enrolment_result = {"status": "enrolled", "count": len(enrolments)}

    return {
        "course_id": course_id,
        "dry_run": dry_run,
        "planned": planned,
        "created_sections": created_sections,
        "created_activities": created_activities,
        "enrolment": enrolment_result,
    }


async def generate_with_ollama(
    prompt: str,
    *,
    timeout_seconds: int | None = None,
    num_predict: int | None = None,
    max_chars: int | None = None,
    stop_after_lines: int | None = None,
) -> str:
    timeout = timeout_seconds or settings.ollama_timeout_seconds
    predict = num_predict or settings.ollama_num_predict
    char_limit = max_chars or settings.ollama_max_chars
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": True,
        "options": {
            "num_predict": predict,
            "temperature": settings.ollama_temperature,
        },
    }
    try:
        client_timeout = httpx.Timeout(timeout=timeout, connect=5.0)
        started_at = time.monotonic()
        async with httpx.AsyncClient(timeout=client_timeout) as client:
            async with client.stream(
                "POST", f"{settings.ollama_base_url}/api/generate", json=payload
            ) as response:
                response.raise_for_status()
                chunks: list[str] = []
                async for line in response.aiter_lines():
                    if time.monotonic() - started_at >= timeout:
                        return "".join(chunks).strip()[:char_limit].strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    token = data.get("response", "")
                    if token:
                        chunks.append(token)
                    text = "".join(chunks).strip()
                    if stop_after_lines:
                        non_empty_lines = [line for line in text.splitlines() if line.strip()]
                        if len(non_empty_lines) >= stop_after_lines:
                            return "\n".join(non_empty_lines[:stop_after_lines]).strip()[:char_limit].strip()
                    if len(text) >= char_limit:
                        return text[:char_limit].strip()
                    if data.get("done"):
                        return text
                return "".join(chunks).strip()
    except (httpx.HTTPError, ValueError):
        # Keep orchestrator endpoints available even when the model is not yet pulled.
        return ""


async def run_assessment(payload: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(f"{settings.runner_base_url}/evaluate", json=payload)
        response.raise_for_status()
        return response.json()


async def simulator_create_scenario(payload: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{settings.simulator_base_url}/sim/v1/scenarios/create",
            json={"payload": payload},
        )
        response.raise_for_status()
        return response.json()


async def simulator_list_templates() -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(f"{settings.simulator_base_url}/sim/v1/scenarios/templates")
        response.raise_for_status()
        return response.json()


async def simulator_create_from_template(
    template_id: str, tenant_id: str, scenario_id: str, connector_type: str
) -> dict[str, Any]:
    params = {
        "tenant_id": tenant_id,
        "scenario_id": scenario_id,
        "connector_type": connector_type,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{settings.simulator_base_url}/sim/v1/scenarios/templates/{template_id}/create",
            params=params,
        )
        response.raise_for_status()
        return response.json()


async def simulator_run_scenario(scenario_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{settings.simulator_base_url}/sim/v1/scenarios/{scenario_id}/run"
        )
        response.raise_for_status()
        return response.json()


async def simulator_replay_scenario(scenario_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{settings.simulator_base_url}/sim/v1/scenarios/{scenario_id}/replay"
        )
        response.raise_for_status()
        return response.json()


async def simulator_pause_scenario(scenario_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{settings.simulator_base_url}/sim/v1/scenarios/{scenario_id}/pause"
        )
        response.raise_for_status()
        return response.json()


async def simulator_resume_scenario(scenario_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{settings.simulator_base_url}/sim/v1/scenarios/{scenario_id}/resume"
        )
        response.raise_for_status()
        return response.json()


async def simulator_get_status(scenario_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(
            f"{settings.simulator_base_url}/sim/v1/scenarios/{scenario_id}/status"
        )
        response.raise_for_status()
        return response.json()


async def simulator_list_connectors() -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(f"{settings.simulator_base_url}/sim/v1/connectors")
        response.raise_for_status()
        return response.json()


async def simulator_configure_connector(payload: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{settings.simulator_base_url}/sim/v1/connectors/configure",
            json={"payload": payload},
        )
        response.raise_for_status()
        return response.json()


async def simulator_get_connector(tenant_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(
            f"{settings.simulator_base_url}/sim/v1/connectors/{tenant_id}"
        )
        response.raise_for_status()
        return response.json()


async def simulator_delete_connector(tenant_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.delete(
            f"{settings.simulator_base_url}/sim/v1/connectors/{tenant_id}"
        )
        response.raise_for_status()
        return response.json()


async def simulator_get_report(scenario_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(
            f"{settings.simulator_base_url}/sim/v1/scenarios/{scenario_id}/report"
        )
        response.raise_for_status()
        return response.json()


async def simulator_purge_scenario(scenario_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.delete(
            f"{settings.simulator_base_url}/sim/v1/scenarios/{scenario_id}/purge"
        )
        response.raise_for_status()
        return response.json()


async def sync_to_moodle(payload: dict[str, Any]) -> dict[str, Any]:
    # This keeps existing assessment behavior compatible while sending structured output.
    return {
        "status": "queued",
        "moodle_base_url": settings.moodle_base_url,
        "payload": payload,
    }
