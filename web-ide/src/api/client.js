const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function generateModule(topic) {
  const response = await fetch(`${API_BASE}/learning/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic, level: "beginner", goals: ["build confidence"] }),
  });

  if (!response.ok) {
    throw new Error("Unable to generate module.");
  }
  return response.json();
}

export async function evaluateSubmission(payload) {
  const response = await fetch(`${API_BASE}/assessment/evaluate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Evaluation failed.");
  }
  return response.json();
}
