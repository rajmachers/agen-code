from __future__ import annotations

import hashlib
import time

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Assessment Runner",
    description="Executes coding assessments and returns deterministic metrics.",
    version="0.1.0",
)


class EvaluatePayload(BaseModel):
    assignment_id: str
    learner_id: str
    language: str
    repo_url: str
    commit_hash: str
    tests_path: str = "tests"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/evaluate")
def evaluate(payload: EvaluatePayload) -> dict[str, float | int]:
    # MVP deterministic scoring based on commit hash for repeatable demos.
    digest = hashlib.sha256(payload.commit_hash.encode("utf-8")).hexdigest()
    normalized = int(digest[:8], 16) / 0xFFFFFFFF

    test_pass_rate = round(0.4 + (normalized * 0.6), 2)
    execution_ms = int(120 + normalized * 900)
    memory_mb = int(30 + normalized * 140)

    time.sleep(0.05)

    return {
        "test_pass_rate": test_pass_rate,
        "execution_ms": execution_ms,
        "memory_mb": memory_mb,
    }
