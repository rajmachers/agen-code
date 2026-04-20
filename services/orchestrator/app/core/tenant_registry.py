from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock


@dataclass
class TenantRecord:
    tenant_id: str
    name: str
    quotas: dict[str, int] = field(default_factory=lambda: {
        "context_generations_daily": 200,
        "evidence_sessions_daily": 1000,
        "handover_daily": 1000,
    })


_LOCK = Lock()
_TENANTS: dict[str, TenantRecord] = {}
_TENANT_USERS: dict[str, dict[str, set[str]]] = {}


def create_tenant(tenant_id: str, name: str, quotas: dict[str, int] | None = None) -> TenantRecord:
    with _LOCK:
        if tenant_id in _TENANTS:
            raise ValueError(f"Tenant already exists: {tenant_id}")
        record = TenantRecord(tenant_id=tenant_id, name=name)
        if quotas:
            record.quotas.update(quotas)
        _TENANTS[tenant_id] = record
        _TENANT_USERS.setdefault(tenant_id, {})
        return record


def list_tenants() -> list[TenantRecord]:
    with _LOCK:
        return list(_TENANTS.values())


def get_tenant(tenant_id: str) -> TenantRecord | None:
    with _LOCK:
        return _TENANTS.get(tenant_id)


def upsert_tenant_user_roles(tenant_id: str, user_id: str, roles: list[str]) -> dict[str, list[str]]:
    with _LOCK:
        if tenant_id not in _TENANTS:
            raise KeyError("Tenant not found")
        members = _TENANT_USERS.setdefault(tenant_id, {})
        members[user_id] = set(roles)
        return {"user_id": user_id, "roles": sorted(members[user_id])}


def list_tenant_user_roles(tenant_id: str) -> list[dict[str, list[str] | str]]:
    with _LOCK:
        if tenant_id not in _TENANTS:
            raise KeyError("Tenant not found")
        members = _TENANT_USERS.setdefault(tenant_id, {})
        return [
            {"user_id": user_id, "roles": sorted(roles)}
            for user_id, roles in sorted(members.items())
        ]
