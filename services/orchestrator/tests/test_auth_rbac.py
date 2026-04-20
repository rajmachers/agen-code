from fastapi.testclient import TestClient

from app.main import app


def test_auth_me_returns_identity_when_auth_disabled() -> None:
    client = TestClient(app)
    response = client.get("/auth/me")

    assert response.status_code == 200
    payload = response.json()
    assert payload["subject"] == "dev-user"
    assert "super_admin" in payload["roles"]


def test_auth_enabled_requires_token(monkeypatch) -> None:
    monkeypatch.setattr("app.core.config.settings.auth_enabled", True)
    client = TestClient(app)

    response = client.get("/auth/me")

    assert response.status_code == 401


def test_auth_enabled_accepts_active_token(monkeypatch) -> None:
    async def fake_introspect(_token: str):
        return {
            "active": True,
            "sub": "user-1",
            "preferred_username": "tenant_admin_1",
            "email": "tenant-admin@example.com",
            "roles": ["tenant_admin"],
            "tenant_id": "tenant_01",
        }

    monkeypatch.setattr("app.core.config.settings.auth_enabled", True)
    monkeypatch.setattr("app.core.security._introspect_token", fake_introspect)
    client = TestClient(app)

    response = client.get("/auth/me", headers={"Authorization": "Bearer token-123"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["subject"] == "user-1"
    assert payload["tenant_ids"] == ["tenant_01"]


def test_tenant_user_cannot_access_other_tenant_connector(monkeypatch) -> None:
    async def fake_introspect(_token: str):
        return {
            "active": True,
            "sub": "user-2",
            "preferred_username": "integration_user",
            "roles": ["integration_manager"],
            "tenant_id": "tenant_01",
        }

    async def fake_get_connector(_tenant_id: str):
        return {"tenantId": _tenant_id, "status": "configured"}

    monkeypatch.setattr("app.core.config.settings.auth_enabled", True)
    monkeypatch.setattr("app.core.security._introspect_token", fake_introspect)
    monkeypatch.setattr("app.routers.simulator.simulator_get_connector", fake_get_connector)

    client = TestClient(app)
    response = client.get(
        "/simulator/connectors/tenant_02",
        headers={"Authorization": "Bearer token-abc"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Cross-tenant access denied"
