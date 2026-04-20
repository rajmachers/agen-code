const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

let authContext = {
  token: "",
  tenantId: "",
};

export function setApiAuthContext(next) {
  authContext = {
    token: next?.token || "",
    tenantId: next?.tenantId || "",
  };
}

async function requestJson(path, options = {}) {
  const authHeaders = {};
  if (authContext.token) {
    authHeaders.Authorization = `Bearer ${authContext.token}`;
  }
  if (authContext.tenantId) {
    authHeaders["x-tenant-id"] = authContext.tenantId;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...authHeaders,
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const errorPayload = await response.json();
      message = errorPayload.detail || JSON.stringify(errorPayload);
    } catch {
      // Ignore JSON parse errors and use fallback message.
    }
    throw new Error(message);
  }

  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    return null;
  }
  return response.json();
}

export async function generateModule(topic) {
  return requestJson("/learning/generate", {
    method: "POST",
    body: JSON.stringify({ topic, level: "beginner", goals: ["build confidence"] }),
  });
}

export async function evaluateSubmission(payload) {
  return requestJson("/assessment/evaluate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listSimulatorTemplates() {
  return requestJson("/simulator/scenarios/templates");
}

export async function createScenarioFromTemplate(templateId, payload) {
  return requestJson(`/simulator/scenarios/templates/${templateId}`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function createScenario(scenarioPayload) {
  return requestJson("/simulator/scenarios", {
    method: "POST",
    body: JSON.stringify({ scenario: scenarioPayload }),
  });
}

export async function runScenario(scenarioId) {
  return requestJson(`/simulator/scenarios/${scenarioId}/run`, { method: "POST" });
}

export async function replayScenario(scenarioId) {
  return requestJson(`/simulator/scenarios/${scenarioId}/replay`, { method: "POST" });
}

export async function pauseScenario(scenarioId) {
  return requestJson(`/simulator/scenarios/${scenarioId}/pause`, { method: "POST" });
}

export async function resumeScenario(scenarioId) {
  return requestJson(`/simulator/scenarios/${scenarioId}/resume`, { method: "POST" });
}

export async function getScenarioStatus(scenarioId) {
  return requestJson(`/simulator/scenarios/${scenarioId}/status`);
}

export async function getScenarioReport(scenarioId) {
  return requestJson(`/simulator/scenarios/${scenarioId}/report`);
}

export async function purgeScenario(scenarioId) {
  return requestJson(`/simulator/scenarios/${scenarioId}/purge`, { method: "DELETE" });
}

export async function listConnectors() {
  return requestJson("/simulator/connectors");
}

export async function configureConnector(connectorPayload) {
  return requestJson("/simulator/connectors/configure", {
    method: "POST",
    body: JSON.stringify({ connector: connectorPayload }),
  });
}

export async function getConnector(tenantId) {
  return requestJson(`/simulator/connectors/${tenantId}`);
}

export async function deleteConnector(tenantId) {
  return requestJson(`/simulator/connectors/${tenantId}`, { method: "DELETE" });
}

export async function returnToLms(payload) {
  return requestJson("/delivery/handover/return-to-lms", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
