from __future__ import annotations

import json
import time
from typing import Any

import httpx

from app.core.config import settings


async def generate_with_ollama(
    prompt: str,
    *,
    timeout_seconds: int | None = None,
    num_predict: int | None = None,
    max_chars: int | None = None,
    stop_after_lines: int | None = None,
) -> str:
    timeout = timeout_seconds or settings.ollama_timeout_seconds
    predict = num_predict or settings.ollama_num_predict
    char_limit = max_chars or settings.ollama_max_chars
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": True,
        "options": {
            "num_predict": predict,
            "temperature": settings.ollama_temperature,
        },
    }
    try:
        client_timeout = httpx.Timeout(timeout=timeout, connect=5.0)
        started_at = time.monotonic()
        async with httpx.AsyncClient(timeout=client_timeout) as client:
            async with client.stream(
                "POST", f"{settings.ollama_base_url}/api/generate", json=payload
            ) as response:
                response.raise_for_status()
                chunks: list[str] = []
                async for line in response.aiter_lines():
                    if time.monotonic() - started_at >= timeout:
                        return "".join(chunks).strip()[:char_limit].strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    token = data.get("response", "")
                    if token:
                        chunks.append(token)
                    text = "".join(chunks).strip()
                    if stop_after_lines:
                        non_empty_lines = [line for line in text.splitlines() if line.strip()]
                        if len(non_empty_lines) >= stop_after_lines:
                            return "\n".join(non_empty_lines[:stop_after_lines]).strip()[:char_limit].strip()
                    if len(text) >= char_limit:
                        return text[:char_limit].strip()
                    if data.get("done"):
                        return text
                return "".join(chunks).strip()
    except (httpx.HTTPError, ValueError):
        # Keep orchestrator endpoints available even when the model is not yet pulled.
        return ""


async def run_assessment(payload: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(f"{settings.runner_base_url}/evaluate", json=payload)
        response.raise_for_status()
        return response.json()


async def simulator_create_scenario(payload: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{settings.simulator_base_url}/sim/v1/scenarios/create",
            json={"payload": payload},
        )
        response.raise_for_status()
        return response.json()


async def simulator_list_templates() -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(f"{settings.simulator_base_url}/sim/v1/scenarios/templates")
        response.raise_for_status()
        return response.json()


async def simulator_create_from_template(
    template_id: str, tenant_id: str, scenario_id: str, connector_type: str
) -> dict[str, Any]:
    params = {
        "tenant_id": tenant_id,
        "scenario_id": scenario_id,
        "connector_type": connector_type,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{settings.simulator_base_url}/sim/v1/scenarios/templates/{template_id}/create",
            params=params,
        )
        response.raise_for_status()
        return response.json()


async def simulator_run_scenario(scenario_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{settings.simulator_base_url}/sim/v1/scenarios/{scenario_id}/run"
        )
        response.raise_for_status()
        return response.json()


async def simulator_replay_scenario(scenario_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{settings.simulator_base_url}/sim/v1/scenarios/{scenario_id}/replay"
        )
        response.raise_for_status()
        return response.json()


async def simulator_pause_scenario(scenario_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{settings.simulator_base_url}/sim/v1/scenarios/{scenario_id}/pause"
        )
        response.raise_for_status()
        return response.json()


async def simulator_resume_scenario(scenario_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{settings.simulator_base_url}/sim/v1/scenarios/{scenario_id}/resume"
        )
        response.raise_for_status()
        return response.json()


async def simulator_get_status(scenario_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(
            f"{settings.simulator_base_url}/sim/v1/scenarios/{scenario_id}/status"
        )
        response.raise_for_status()
        return response.json()


async def simulator_list_connectors() -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(f"{settings.simulator_base_url}/sim/v1/connectors")
        response.raise_for_status()
        return response.json()


async def simulator_configure_connector(payload: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{settings.simulator_base_url}/sim/v1/connectors/configure",
            json={"payload": payload},
        )
        response.raise_for_status()
        return response.json()


async def simulator_get_connector(tenant_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(
            f"{settings.simulator_base_url}/sim/v1/connectors/{tenant_id}"
        )
        response.raise_for_status()
        return response.json()


async def simulator_delete_connector(tenant_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.delete(
            f"{settings.simulator_base_url}/sim/v1/connectors/{tenant_id}"
        )
        response.raise_for_status()
        return response.json()


async def simulator_get_report(scenario_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(
            f"{settings.simulator_base_url}/sim/v1/scenarios/{scenario_id}/report"
        )
        response.raise_for_status()
        return response.json()


async def sync_to_moodle(payload: dict[str, Any]) -> dict[str, Any]:
    # Replace with Moodle webservice endpoint in production.
    return {
        "status": "queued",
        "moodle_base_url": settings.moodle_base_url,
        "payload": payload,
    }
