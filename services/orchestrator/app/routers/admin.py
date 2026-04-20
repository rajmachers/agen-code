from fastapi import APIRouter, Depends, HTTPException

from app.core.metering import get_tenant_metering
from app.core.security import AuthContext, ensure_tenant_access, require_roles
from app.core.tenant_registry import (
    create_tenant,
    get_tenant,
    list_tenant_user_roles,
    list_tenants,
    upsert_tenant_user_roles,
)
from app.schemas import (
    TenantCreateRequest,
    TenantImpersonationRequest,
    TenantUserRolesRequest,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/tenants")
async def create_tenant_endpoint(
    payload: TenantCreateRequest,
    _auth: AuthContext = Depends(require_roles("super_admin")),
) -> dict:
    try:
        tenant = create_tenant(payload.tenant_id, payload.name, payload.quotas)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return {
        "tenant_id": tenant.tenant_id,
        "name": tenant.name,
        "quotas": tenant.quotas,
    }


@router.get("/tenants")
async def list_tenants_endpoint(
    auth: AuthContext = Depends(require_roles("tenant_admin", "super_admin")),
) -> dict:
    rows = list_tenants()
    if auth.is_super_admin:
        return {
            "count": len(rows),
            "items": [
                {"tenant_id": row.tenant_id, "name": row.name, "quotas": row.quotas}
                for row in rows
            ],
            "view_mode": "global",
        }

    scoped = [row for row in rows if row.tenant_id in auth.tenant_ids]
    return {
        "count": len(scoped),
        "items": [
            {"tenant_id": row.tenant_id, "name": row.name, "quotas": row.quotas}
            for row in scoped
        ],
        "view_mode": "tenant",
    }


@router.post("/tenants/{tenant_id}/users/{user_id}/roles")
async def upsert_tenant_user_roles_endpoint(
    tenant_id: str,
    user_id: str,
    payload: TenantUserRolesRequest,
    auth: AuthContext = Depends(require_roles("tenant_admin", "super_admin")),
) -> dict:
    ensure_tenant_access(auth, tenant_id)
    try:
        row = upsert_tenant_user_roles(tenant_id=tenant_id, user_id=user_id, roles=payload.roles)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"tenant_id": tenant_id, **row}


@router.get("/tenants/{tenant_id}/users")
async def list_tenant_users_endpoint(
    tenant_id: str,
    auth: AuthContext = Depends(require_roles("tenant_admin", "super_admin")),
) -> dict:
    ensure_tenant_access(auth, tenant_id)
    try:
        rows = list_tenant_user_roles(tenant_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"tenant_id": tenant_id, "count": len(rows), "items": rows}


@router.post("/impersonate")
async def impersonate_tenant_view(
    payload: TenantImpersonationRequest,
    auth: AuthContext = Depends(require_roles("super_admin")),
) -> dict:
    tenant = get_tenant(payload.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return {
        "actor": auth.username or auth.subject,
        "mode": "impersonated_tenant",
        "tenant_id": payload.tenant_id,
        "assumed_roles": payload.assumed_roles,
        "note": "Use this context in frontend to render exact tenant-scoped view.",
    }


@router.get("/tenants/{tenant_id}/metering")
async def get_tenant_metering_endpoint(
    tenant_id: str,
    auth: AuthContext = Depends(require_roles("tenant_admin", "super_admin")),
) -> dict:
    ensure_tenant_access(auth, tenant_id)
    try:
        return get_tenant_metering(tenant_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
