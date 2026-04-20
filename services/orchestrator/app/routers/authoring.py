from __future__ import annotations

import re
from threading import Lock
from uuid import uuid4

import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.core.metering import QuotaExceededError, consume_quota
from app.core.security import AuthContext, ensure_tenant_access, require_roles
from app.core.tenant_registry import get_tenant
from app.schemas import ContextBridgeGenerateRequest

router = APIRouter(prefix="/authoring", tags=["authoring"])

_DRAFTS_LOCK = Lock()
_DRAFTS: dict[str, dict] = {}


def _strip_html(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", value).strip()


async def _resolve_source_text(payload: ContextBridgeGenerateRequest) -> str:
    if payload.source_type == "readme":
        return payload.source.strip()

    async with httpx.AsyncClient(timeout=8.0) as client:
        response = await client.get(payload.source)
    response.raise_for_status()
    text = response.text
    return _strip_html(text)[:5000]


def _build_track_summary(source_text: str, level: str) -> dict:
    terms = [token for token in re.split(r"[^a-zA-Z0-9_]+", source_text.lower()) if len(token) > 4]
    frequency: dict[str, int] = {}
    for token in terms:
        frequency[token] = frequency.get(token, 0) + 1
    top_terms = [item[0] for item in sorted(frequency.items(), key=lambda pair: pair[1], reverse=True)[:6]]

    objectives = [
        f"Explain and apply {top_terms[0] if len(top_terms) > 0 else 'core concepts'}",
        f"Build practical coding tasks at {level} level",
        f"Assess correctness and reasoning with rubric-backed checkpoints",
    ]
    tasks = [
        {"type": "practice", "title": "Warm-up drill", "difficulty": "easy"},
        {"type": "assignment", "title": "Context-driven assignment", "difficulty": level},
        {"type": "project", "title": "Mini integration project", "difficulty": "hard"},
    ]
    return {"keywords": top_terms, "objectives": objectives, "tasks": tasks}


@router.post("/context-bridge/generate")
async def generate_from_context_bridge(
    payload: ContextBridgeGenerateRequest,
    auth: AuthContext = Depends(require_roles("tenant_admin", "teacher", "sme", "reviewer")),
) -> dict:
    ensure_tenant_access(auth, payload.tenant_id)
    if get_tenant(payload.tenant_id) is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    try:
        metering = consume_quota(payload.tenant_id, "context_generations_daily", amount=1)
    except QuotaExceededError as error:
        raise HTTPException(status_code=429, detail=str(error)) from error

    source_text = await _resolve_source_text(payload)
    plan = _build_track_summary(source_text=source_text, level=payload.level)
    draft_id = str(uuid4())
    draft = {
        "draft_id": draft_id,
        "tenant_id": payload.tenant_id,
        "title": payload.title_hint or "Zero-Shot Generated Track",
        "status": "draft",
        "source_type": payload.source_type,
        "keywords": plan["keywords"],
        "objectives": plan["objectives"],
        "tasks": plan["tasks"],
        "metering": metering,
    }
    with _DRAFTS_LOCK:
        _DRAFTS[draft_id] = draft
    return draft


@router.get("/drafts/{draft_id}")
async def get_draft(
    draft_id: str,
    auth: AuthContext = Depends(require_roles("tenant_admin", "teacher", "sme", "reviewer")),
) -> dict:
    with _DRAFTS_LOCK:
        draft = _DRAFTS.get(draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Draft not found")
    ensure_tenant_access(auth, str(draft.get("tenant_id")))
    return draft


@router.post("/drafts/{draft_id}/submit-review")
async def submit_draft_review(
    draft_id: str,
    auth: AuthContext = Depends(require_roles("tenant_admin", "teacher", "sme")),
) -> dict:
    with _DRAFTS_LOCK:
        draft = _DRAFTS.get(draft_id)
        if draft is None:
            raise HTTPException(status_code=404, detail="Draft not found")
        ensure_tenant_access(auth, str(draft.get("tenant_id")))
        draft["status"] = "in_review"
    return draft


@router.post("/drafts/{draft_id}/approve")
async def approve_draft(
    draft_id: str,
    auth: AuthContext = Depends(require_roles("tenant_admin", "reviewer")),
) -> dict:
    with _DRAFTS_LOCK:
        draft = _DRAFTS.get(draft_id)
        if draft is None:
            raise HTTPException(status_code=404, detail="Draft not found")
        ensure_tenant_access(auth, str(draft.get("tenant_id")))
        draft["status"] = "approved"
    return draft
