from __future__ import annotations

from datetime import date, datetime, timezone
from threading import Lock

from app.core.tenant_registry import get_tenant


class QuotaExceededError(RuntimeError):
    pass


_LOCK = Lock()
_COUNTERS: dict[str, dict[str, int]] = {}
_COUNTER_DAY: str | None = None


def _today() -> str:
    return date.today().isoformat()


def _ensure_day_rollover() -> None:
    global _COUNTER_DAY
    today = _today()
    if _COUNTER_DAY != today:
        _COUNTERS.clear()
        _COUNTER_DAY = today


def consume_quota(tenant_id: str, key: str, amount: int = 1) -> dict[str, int | str]:
    tenant = get_tenant(tenant_id)
    if tenant is None:
        raise KeyError("Tenant not found")

    limit = int(tenant.quotas.get(key, 0))
    if limit <= 0:
        raise QuotaExceededError(f"Quota disabled for {key}")

    with _LOCK:
        _ensure_day_rollover()
        tenant_counters = _COUNTERS.setdefault(tenant_id, {})
        current = int(tenant_counters.get(key, 0))
        next_value = current + amount
        if next_value > limit:
            raise QuotaExceededError(f"Quota exceeded for {key}: {next_value}/{limit}")
        tenant_counters[key] = next_value
        return {
            "tenant_id": tenant_id,
            "key": key,
            "used": next_value,
            "limit": limit,
            "window": _COUNTER_DAY or _today(),
        }


def get_tenant_metering(tenant_id: str) -> dict[str, object]:
    tenant = get_tenant(tenant_id)
    if tenant is None:
        raise KeyError("Tenant not found")

    with _LOCK:
        _ensure_day_rollover()
        used = dict(_COUNTERS.get(tenant_id, {}))

    now = datetime.now(timezone.utc).isoformat()
    return {
        "tenant_id": tenant_id,
        "window": _COUNTER_DAY or _today(),
        "generated_at": now,
        "limits": dict(tenant.quotas),
        "used": used,
    }
