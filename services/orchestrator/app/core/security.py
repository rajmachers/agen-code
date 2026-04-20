from dataclasses import dataclass
from typing import Any

import httpx
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthContext:
    subject: str
    username: str | None
    email: str | None
    roles: set[str]
    tenant_ids: set[str]
    claims: dict[str, Any]

    @property
    def is_super_admin(self) -> bool:
        return settings.auth_claim_super_admin_role in self.roles


def _default_auth_context() -> AuthContext:
    # Development fallback when auth is disabled.
    return AuthContext(
        subject="dev-user",
        username="dev-user",
        email=None,
        roles={settings.auth_claim_super_admin_role},
        tenant_ids={"*"},
        claims={},
    )


def _keycloak_introspect_url() -> str:
    return (
        f"{settings.keycloak_base_url.rstrip('/')}/realms/"
        f"{settings.keycloak_realm}/protocol/openid-connect/token/introspect"
    )


def _collect_roles(claims: dict[str, Any]) -> set[str]:
    roles: set[str] = set()

    direct_roles = claims.get(settings.auth_claim_roles)
    if isinstance(direct_roles, list):
        roles.update(str(item) for item in direct_roles)

    realm_access = claims.get("realm_access")
    if isinstance(realm_access, dict):
        realm_roles = realm_access.get("roles")
        if isinstance(realm_roles, list):
            roles.update(str(item) for item in realm_roles)

    resource_access = claims.get("resource_access")
    if isinstance(resource_access, dict):
        client_access = resource_access.get(settings.keycloak_client_id)
        if isinstance(client_access, dict):
            client_roles = client_access.get("roles")
            if isinstance(client_roles, list):
                roles.update(str(item) for item in client_roles)

    return roles


def _collect_tenants(claims: dict[str, Any]) -> set[str]:
    tenant_ids: set[str] = set()

    single_tenant = claims.get(settings.auth_claim_tenant)
    if isinstance(single_tenant, str) and single_tenant:
        tenant_ids.add(single_tenant)

    multi_tenants = claims.get(settings.auth_claim_tenants)
    if isinstance(multi_tenants, list):
        tenant_ids.update(str(item) for item in multi_tenants if item)

    org_id = claims.get("org_id")
    if isinstance(org_id, str) and org_id:
        tenant_ids.add(org_id)

    return tenant_ids


async def _introspect_token(token: str) -> dict[str, Any]:
    payload = {
        "token": token,
        "client_id": settings.keycloak_client_id,
        "client_secret": settings.keycloak_client_secret,
    }
    async with httpx.AsyncClient(timeout=8.0, verify=settings.keycloak_verify_ssl) as client:
        response = await client.post(_keycloak_introspect_url(), data=payload)
    response.raise_for_status()
    parsed = response.json()
    if not isinstance(parsed, dict):
        raise HTTPException(status_code=401, detail="Invalid token introspection response")
    return parsed


async def get_auth_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> AuthContext:
    if not settings.auth_enabled:
        return _default_auth_context()

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    try:
        claims = await _introspect_token(credentials.credentials)
    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {error}",
        ) from error

    if not claims.get("active"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive token")

    roles = _collect_roles(claims)
    tenants = _collect_tenants(claims)

    subject = str(claims.get("sub") or claims.get("username") or "unknown")
    username = claims.get("preferred_username") or claims.get("username")
    email = claims.get("email")

    return AuthContext(
        subject=subject,
        username=str(username) if username else None,
        email=str(email) if email else None,
        roles=roles,
        tenant_ids=tenants,
        claims=claims,
    )


def require_roles(*required_roles: str):
    async def _dependency(auth: AuthContext = Depends(get_auth_context)) -> AuthContext:
        if auth.is_super_admin:
            return auth
        if not set(required_roles).intersection(auth.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role privileges",
            )
        return auth

    return _dependency


def ensure_tenant_access(auth: AuthContext, tenant_id: str) -> None:
    if auth.is_super_admin:
        return
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Missing tenant identifier")
    if tenant_id not in auth.tenant_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cross-tenant access denied",
        )


def ensure_header_tenant_access(auth: AuthContext, header_tenant_id: str | None) -> str:
    if auth.is_super_admin and header_tenant_id:
        return header_tenant_id

    if not header_tenant_id:
        if auth.tenant_ids:
            # Non-super users can infer default tenant when exactly one assignment exists.
            if len(auth.tenant_ids) == 1:
                return next(iter(auth.tenant_ids))
        raise HTTPException(status_code=400, detail="Missing tenant header")

    ensure_tenant_access(auth, header_tenant_id)
    return header_tenant_id


async def get_tenant_header(
    tenant_id: str | None = Header(default=None, alias=settings.auth_header_tenant),
) -> str | None:
    return tenant_id
