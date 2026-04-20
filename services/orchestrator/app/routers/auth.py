from fastapi import APIRouter, Depends

from app.core.security import AuthContext, get_auth_context

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
async def auth_me(auth: AuthContext = Depends(get_auth_context)) -> dict:
    roles = sorted(auth.roles)

    modules = {
        "super_admin": auth.is_super_admin,
        "tenant_admin": auth.is_super_admin or "tenant_admin" in auth.roles,
        "authoring": auth.is_super_admin
        or bool({"tenant_admin", "sme", "teacher"}.intersection(auth.roles)),
        "delivery": auth.is_super_admin
        or bool({"tenant_admin", "teacher", "candidate", "evaluator"}.intersection(auth.roles)),
        "integrations": auth.is_super_admin
        or bool({"tenant_admin", "integration_manager"}.intersection(auth.roles)),
    }

    return {
        "subject": auth.subject,
        "username": auth.username,
        "email": auth.email,
        "roles": roles,
        "tenant_ids": sorted(auth.tenant_ids),
        "module_access": modules,
    }
