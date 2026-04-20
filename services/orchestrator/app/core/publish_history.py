from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any

from app.core.config import settings

_HISTORY_LOCK = Lock()


def _history_file() -> Path:
    return Path(settings.connector_publish_history_path)


def append_publish_history(record: dict[str, Any]) -> None:
    path = _history_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=True)
    with _HISTORY_LOCK:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def list_publish_history(
    *,
    limit: int = 20,
    tenant_id: str | None = None,
    course_id: int | None = None,
    status: str | None = None,
) -> list[dict[str, Any]]:
    path = _history_file()
    if not path.exists():
        return []

    with _HISTORY_LOCK:
        lines = path.read_text(encoding="utf-8").splitlines()

    items: list[dict[str, Any]] = []
    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if tenant_id is not None and str(row.get("tenant_id")) != tenant_id:
            continue
        if course_id is not None and int(row.get("course_id", -1)) != course_id:
            continue
        if status is not None and str(row.get("status")) != status:
            continue
        items.append(row)
        if len(items) >= limit:
            break
    return items


def get_publish_history_record(request_id: str) -> dict[str, Any] | None:
    path = _history_file()
    if not path.exists():
        return None

    with _HISTORY_LOCK:
        lines = path.read_text(encoding="utf-8").splitlines()

    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if str(row.get("request_id")) == request_id:
            return row
    return None
