import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import uuid4
from datetime import datetime, timezone

from app.core.clients import (
    moodle_get_course_sections,
    moodle_lookup_cohorts,
    moodle_lookup_courses,
    moodle_lookup_users,
    moodle_provision_course_activities,
    moodle_sync_cohort_to_course,
)
from app.core.publish_history import (
    append_publish_history,
    get_publish_history_record,
    list_publish_history,
)
from app.core.security import (
    AuthContext,
    ensure_header_tenant_access,
    get_tenant_header,
    require_roles,
)
from app.schemas import (
    MoodleCatalogueLookupRequest,
    MoodleCohortCourseSyncRequest,
    MoodleCohortLookupRequest,
    MoodleConnectorPublishRequest,
    MoodleCourseProvisionRequest,
    MoodleUserLookupRequest,
)

router = APIRouter(prefix="/connectors", tags=["connectors"])


def _rethrow_connector_error(error: Exception) -> None:
    if isinstance(error, httpx.HTTPStatusError):
        detail = error.response.text or "Moodle request failed"
        raise HTTPException(status_code=error.response.status_code, detail=detail) from error
    raise HTTPException(status_code=400, detail=str(error)) from error


def _error_summary(error: Exception) -> str:
    if isinstance(error, httpx.HTTPStatusError):
        return error.response.text or "Moodle request failed"
    return str(error)


@router.post("/moodle/catalogue/lookup")
async def lookup_catalogue(
    payload: MoodleCatalogueLookupRequest,
    auth: AuthContext = Depends(require_roles("tenant_admin", "teacher", "sme", "integration_manager")),
    tenant_id: str | None = Depends(get_tenant_header),
) -> dict:
    ensure_header_tenant_access(auth, tenant_id)
    try:
        courses = await moodle_lookup_courses(payload.query, payload.limit)
        if not payload.include_sections:
            return {"count": len(courses), "items": courses}

        with_sections = []
        for course in courses:
            course_id = int(course["id"])
            sections = await moodle_get_course_sections(course_id)
            with_sections.append({**course, "sections": sections})
        return {"count": len(with_sections), "items": with_sections}
    except Exception as error:  # noqa: BLE001
        _rethrow_connector_error(error)


@router.post("/moodle/users/lookup")
async def lookup_users(
    payload: MoodleUserLookupRequest,
    auth: AuthContext = Depends(require_roles("tenant_admin", "teacher", "integration_manager")),
    tenant_id: str | None = Depends(get_tenant_header),
) -> dict:
    ensure_header_tenant_access(auth, tenant_id)
    try:
        users = await moodle_lookup_users(payload.query, payload.limit)
        return {"count": len(users), "items": users}
    except Exception as error:  # noqa: BLE001
        _rethrow_connector_error(error)


@router.post("/moodle/cohorts/lookup")
async def lookup_cohorts(
    payload: MoodleCohortLookupRequest,
    auth: AuthContext = Depends(require_roles("tenant_admin", "teacher", "integration_manager")),
    tenant_id: str | None = Depends(get_tenant_header),
) -> dict:
    ensure_header_tenant_access(auth, tenant_id)
    try:
        cohorts = await moodle_lookup_cohorts(payload.query, payload.limit)
        return {"count": len(cohorts), "items": cohorts}
    except Exception as error:  # noqa: BLE001
        _rethrow_connector_error(error)


@router.post("/moodle/cohorts/sync-course")
async def sync_cohort_to_course(
    payload: MoodleCohortCourseSyncRequest,
    auth: AuthContext = Depends(require_roles("tenant_admin", "integration_manager")),
    tenant_id: str | None = Depends(get_tenant_header),
) -> dict:
    ensure_header_tenant_access(auth, tenant_id)
    try:
        return await moodle_sync_cohort_to_course(
            cohort_id=payload.cohort_id,
            course_id=payload.course_id,
            role_id=payload.role_id,
            dry_run=payload.dry_run,
        )
    except Exception as error:  # noqa: BLE001
        _rethrow_connector_error(error)


@router.post("/moodle/courses/provision")
async def provision_course(
    payload: MoodleCourseProvisionRequest,
    auth: AuthContext = Depends(require_roles("tenant_admin", "teacher", "sme", "integration_manager")),
    tenant_id: str | None = Depends(get_tenant_header),
) -> dict:
    ensure_header_tenant_access(auth, tenant_id)
    try:
        return await moodle_provision_course_activities(
            course_id=payload.course_id,
            activities=[activity.model_dump() for activity in payload.activities],
            user_ids=payload.user_ids,
            role_id=payload.role_id,
            dry_run=payload.dry_run,
        )
    except Exception as error:  # noqa: BLE001
        _rethrow_connector_error(error)


@router.post("/moodle/publish")
async def publish_to_moodle(
    payload: MoodleConnectorPublishRequest,
    auth: AuthContext = Depends(require_roles("tenant_admin", "integration_manager")),
    tenant_id: str | None = Depends(get_tenant_header),
) -> dict:
    scoped_tenant_id = ensure_header_tenant_access(auth, tenant_id)
    request_id = str(uuid4())
    result: dict = {
        "request_id": request_id,
        "tenant_id": scoped_tenant_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "course_id": payload.course_id,
        "dry_run": payload.dry_run,
        "status": "completed",
        "steps": [],
    }

    try:
        provision_output = await moodle_provision_course_activities(
            course_id=payload.course_id,
            activities=[activity.model_dump() for activity in payload.activities],
            user_ids=payload.user_ids,
            role_id=payload.role_id,
            dry_run=payload.dry_run,
        )
        result["steps"].append(
            {
                "name": "course_provision",
                "status": "completed",
                "output": provision_output,
            }
        )
    except Exception as error:  # noqa: BLE001
        result["steps"].append(
            {
                "name": "course_provision",
                "status": "failed",
                "error": _error_summary(error),
            }
        )
        result["status"] = "failed"
        if payload.stop_on_error:
            append_publish_history(
                {
                    **result,
                    "cohort_id": payload.cohort_id,
                    "request": payload.model_dump(),
                }
            )
            return result

    if payload.cohort_id is not None:
        try:
            cohort_sync_output = await moodle_sync_cohort_to_course(
                cohort_id=payload.cohort_id,
                course_id=payload.course_id,
                role_id=payload.role_id,
                dry_run=payload.dry_run,
            )
            result["steps"].append(
                {
                    "name": "cohort_sync",
                    "status": "completed",
                    "output": cohort_sync_output,
                }
            )
        except Exception as error:  # noqa: BLE001
            result["steps"].append(
                {
                    "name": "cohort_sync",
                    "status": "failed",
                    "error": _error_summary(error),
                }
            )
            result["status"] = "failed"

    append_publish_history(
        {
            **result,
            "cohort_id": payload.cohort_id,
            "request": payload.model_dump(),
        }
    )
    return result


@router.get("/moodle/publish/history")
async def get_publish_history(
    limit: int = Query(default=20, ge=1, le=200),
    course_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    auth: AuthContext = Depends(require_roles("tenant_admin", "teacher", "sme", "integration_manager")),
    tenant_id: str | None = Depends(get_tenant_header),
) -> dict:
    scoped_tenant_id = ensure_header_tenant_access(auth, tenant_id)
    items = list_publish_history(
        limit=limit,
        tenant_id=scoped_tenant_id,
        course_id=course_id,
        status=status,
    )
    return {"count": len(items), "items": items}


@router.get("/moodle/publish/history/{request_id}")
async def get_publish_history_by_id(
    request_id: str,
    auth: AuthContext = Depends(require_roles("tenant_admin", "teacher", "sme", "integration_manager")),
    tenant_id: str | None = Depends(get_tenant_header),
) -> dict:
    scoped_tenant_id = ensure_header_tenant_access(auth, tenant_id)
    row = get_publish_history_record(request_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Publish request not found")
    if row.get("tenant_id") != scoped_tenant_id and not auth.is_super_admin:
        raise HTTPException(status_code=403, detail="Cross-tenant access denied")
    return row
