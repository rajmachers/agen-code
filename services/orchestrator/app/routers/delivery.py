from fastapi import APIRouter, Depends, HTTPException

from app.core.evidence import get_evidence_session
from app.core.metering import QuotaExceededError, consume_quota
from app.core.security import AuthContext, ensure_tenant_access, require_roles
from app.core.tenant_registry import get_tenant
from app.schemas import HandoverToLmsRequest

router = APIRouter(prefix="/delivery", tags=["delivery"])


@router.post("/handover/return-to-lms")
async def return_to_lms(
    payload: HandoverToLmsRequest,
    auth: AuthContext = Depends(require_roles("tenant_admin", "teacher", "evaluator", "candidate")),
) -> dict:
    ensure_tenant_access(auth, payload.tenant_id)
    if get_tenant(payload.tenant_id) is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if not payload.competencies:
        raise HTTPException(status_code=400, detail="Competency payload is required")

    missing_evidence: list[str] = []
    for item in payload.competencies:
        if item.evidence_session_id:
            session = get_evidence_session(item.evidence_session_id)
            if session is None:
                missing_evidence.append(item.evidence_session_id)

    if missing_evidence:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown evidence_session_id values: {', '.join(missing_evidence)}",
        )

    try:
        metering = consume_quota(payload.tenant_id, "handover_daily", amount=1)
    except QuotaExceededError as error:
        raise HTTPException(status_code=429, detail=str(error)) from error

    avg_score = round(sum(item.score for item in payload.competencies) / len(payload.competencies), 2)
    return {
        "status": "ready_for_lms_return",
        "tenant_id": payload.tenant_id,
        "learner_id": payload.learner_id,
        "assignment_id": payload.assignment_id,
        "competency_count": len(payload.competencies),
        "average_score": avg_score,
        "lms_return_url": payload.lms_return_url,
        "metering": metering,
    }
