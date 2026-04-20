from fastapi import APIRouter, Depends, HTTPException

from app.core.evidence import analyze_evidence, get_evidence_session, ingest_evidence_session
from app.core.metering import QuotaExceededError, consume_quota
from app.core.security import AuthContext, ensure_tenant_access, require_roles
from app.core.tenant_registry import get_tenant
from app.schemas import EvidenceSessionIngestRequest

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.post("/sessions")
async def ingest_session(
    payload: EvidenceSessionIngestRequest,
    auth: AuthContext = Depends(require_roles("tenant_admin", "teacher", "evaluator", "candidate")),
) -> dict:
    ensure_tenant_access(auth, payload.tenant_id)
    if get_tenant(payload.tenant_id) is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if not payload.events:
        raise HTTPException(status_code=400, detail="At least one event is required")

    try:
        metering = consume_quota(payload.tenant_id, "evidence_sessions_daily", amount=1)
    except QuotaExceededError as error:
        raise HTTPException(status_code=429, detail=str(error)) from error

    session = ingest_evidence_session(
        tenant_id=payload.tenant_id,
        learner_id=payload.learner_id,
        assignment_id=payload.assignment_id,
        persona=payload.persona,
        events=[event.model_dump() for event in payload.events],
    )
    return {
        "session_id": session.session_id,
        "tenant_id": session.tenant_id,
        "event_count": len(session.events),
        "metering": metering,
    }


@router.get("/sessions/{session_id}/replay")
async def replay_session(
    session_id: str,
    auth: AuthContext = Depends(require_roles("tenant_admin", "teacher", "reviewer", "evaluator")),
) -> dict:
    session = get_evidence_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    ensure_tenant_access(auth, session.tenant_id)
    return analyze_evidence(session)
