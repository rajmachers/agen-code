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

export function generateContextDraft(payload, token) {
  return requestJson("/authoring/context-bridge/generate", {
    method: "POST",
    body: JSON.stringify(payload),
    token,
  });
}

export function submitDraftReview(draftId, token, tenantId) {
  return requestJson(`/authoring/drafts/${draftId}/submit-review`, {
    method: "POST",
    token,
    tenantId,
  });
}

export function approveDraft(draftId, token, tenantId) {
  return requestJson(`/authoring/drafts/${draftId}/approve`, {
    method: "POST",
    token,
    tenantId,
  });
}

export function runGhostPersona(payload, token, tenantId) {
  return requestJson("/simulator/personas/run", {
    method: "POST",
    body: JSON.stringify(payload),
    token,
    tenantId,
  });
}

export function ingestEvidence(payload, token, tenantId) {
  return requestJson("/evidence/sessions", {
    method: "POST",
    body: JSON.stringify(payload),
    token,
    tenantId,
  });
}

export function replayEvidence(sessionId, token, tenantId) {
  return requestJson(`/evidence/sessions/${sessionId}/replay`, {
    token,
    tenantId,
  });
}
