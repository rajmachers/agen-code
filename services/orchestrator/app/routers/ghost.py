from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.core.evidence import analyze_evidence, ingest_evidence_session
from app.core.metering import QuotaExceededError, consume_quota
from app.core.security import AuthContext, ensure_tenant_access, require_roles
from app.core.tenant_registry import get_tenant
from app.schemas import GhostPersonaRunRequest

router = APIRouter(prefix="/simulator/personas", tags=["simulator-ghost"])


def _persona_events(persona: str) -> list[dict]:
    if persona == "expert":
        return [
            {"ts": 1_000, "event_type": "keypress", "payload": {"chars": 25}},
            {"ts": 2_200, "event_type": "keypress", "payload": {"chars": 40}},
            {"ts": 3_500, "event_type": "run_tests", "payload": {"passed": 5, "failed": 1}},
            {"ts": 5_200, "event_type": "keypress", "payload": {"chars": 35}},
        ]
    if persona == "struggler":
        return [
            {"ts": 1_000, "event_type": "keypress", "payload": {"chars": 8}},
            {"ts": 40_000, "event_type": "keypress", "payload": {"chars": 5}},
            {"ts": 120_000, "event_type": "run_tests", "payload": {"passed": 1, "failed": 6}},
            {"ts": 180_000, "event_type": "keypress", "payload": {"chars": 10}},
        ]
    return [
        {"ts": 1_000, "event_type": "paste", "payload": {"chars": 120}},
        {"ts": 1_700, "event_type": "paste", "payload": {"chars": 95}},
        {"ts": 2_200, "event_type": "paste", "payload": {"chars": 110}},
        {"ts": 3_000, "event_type": "run_tests", "payload": {"passed": 7, "failed": 0}},
    ]


@router.post("/run")
async def run_ghost_persona(
    payload: GhostPersonaRunRequest,
    auth: AuthContext = Depends(require_roles("tenant_admin", "integration_manager", "teacher", "evaluator")),
) -> dict:
    ensure_tenant_access(auth, payload.tenant_id)
    if get_tenant(payload.tenant_id) is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    try:
        metering = consume_quota(payload.tenant_id, "evidence_sessions_daily", amount=1)
    except QuotaExceededError as error:
        raise HTTPException(status_code=429, detail=str(error)) from error

    events = _persona_events(payload.persona)
    session = ingest_evidence_session(
        tenant_id=payload.tenant_id,
        learner_id=payload.learner_id,
        assignment_id=payload.assignment_id,
        persona=payload.persona,
        events=events,
    )
    analysis = analyze_evidence(session)

    return {
        "persona": payload.persona,
        "session_id": session.session_id,
        "tenant_id": payload.tenant_id,
        "event_count": len(events),
        "flags": analysis["flags"],
        "metering": metering,
    }
