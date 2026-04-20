const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function headers(token, tenantId) {
  const out = { "Content-Type": "application/json" };
  if (token) out.Authorization = `Bearer ${token}`;
  if (tenantId) out["x-tenant-id"] = tenantId;
  return out;
}

async function requestJson(path, { token = "", tenantId = "", ...options } = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { ...headers(token, tenantId), ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    let msg = `Request failed (${response.status})`;
    try {
      const payload = await response.json();
      msg = payload.detail || JSON.stringify(payload);
    } catch {
      // Ignore parse errors.
    }
    throw new Error(msg);
  }
  return response.json();
}

export function getAuthMe(token) {
  return requestJson("/auth/me", { token });
}

export function createTenant(payload, token) {
  return requestJson("/admin/tenants", {
    method: "POST",
    body: JSON.stringify(payload),
    token,
  });
}

export function listTenants(token) {
  return requestJson("/admin/tenants", { token });
}

export function impersonateTenant(payload, token) {
  return requestJson("/admin/impersonate", {
    method: "POST",
    body: JSON.stringify(payload),
    token,
  });
}

export function upsertTenantUserRoles(tenantId, userId, roles, token) {
  return requestJson(`/admin/tenants/${tenantId}/users/${userId}/roles`, {
    method: "POST",
    body: JSON.stringify({ roles }),
    token,
    tenantId,
  });
}

export function getTenantUsers(tenantId, token) {
  return requestJson(`/admin/tenants/${tenantId}/users`, {
    token,
    tenantId,
  });
}

export function getTenantMetering(tenantId, token) {
  return requestJson(`/admin/tenants/${tenantId}/metering`, {
    token,
    tenantId,
  });
}
