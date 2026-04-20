from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Any
from uuid import uuid4


@dataclass
class EvidenceSession:
    session_id: str
    tenant_id: str
    learner_id: str
    assignment_id: str
    persona: str | None
    events: list[dict[str, Any]]


_LOCK = Lock()
_SESSIONS: dict[str, EvidenceSession] = {}


def ingest_evidence_session(
    *,
    tenant_id: str,
    learner_id: str,
    assignment_id: str,
    events: list[dict[str, Any]],
    persona: str | None = None,
) -> EvidenceSession:
    session = EvidenceSession(
        session_id=str(uuid4()),
        tenant_id=tenant_id,
        learner_id=learner_id,
        assignment_id=assignment_id,
        persona=persona,
        events=sorted(events, key=lambda row: int(row.get("ts", 0))),
    )
    with _LOCK:
        _SESSIONS[session.session_id] = session
    return session


def get_evidence_session(session_id: str) -> EvidenceSession | None:
    with _LOCK:
        return _SESSIONS.get(session_id)


def analyze_evidence(session: EvidenceSession) -> dict[str, Any]:
    paste_count = 0
    keystroke_count = 0
    longest_idle_ms = 0
    previous_ts: int | None = None

    for event in session.events:
        event_type = str(event.get("event_type") or "")
        ts = int(event.get("ts", 0))

        if event_type == "paste":
            paste_count += 1
        if event_type == "keypress":
            keystroke_count += int(event.get("payload", {}).get("chars", 1))

        if previous_ts is not None and ts > previous_ts:
            longest_idle_ms = max(longest_idle_ms, ts - previous_ts)
        previous_ts = ts

    flags: list[str] = []
    if paste_count >= 3:
        flags.append("copy_paste_heavy")
    if paste_count >= 1 and keystroke_count <= 20:
        flags.append("low_typing_high_paste")
    if longest_idle_ms >= 120_000:
        flags.append("long_idle_gap")

    return {
        "session_id": session.session_id,
        "tenant_id": session.tenant_id,
        "learner_id": session.learner_id,
        "assignment_id": session.assignment_id,
        "persona": session.persona,
        "timeline": session.events,
        "stats": {
            "paste_count": paste_count,
            "keystroke_count": keystroke_count,
            "longest_idle_ms": longest_idle_ms,
        },
        "flags": flags,
    }
