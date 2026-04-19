import httpx
from fastapi import APIRouter, HTTPException

from app.core.clients import (
    simulator_configure_connector,
    simulator_create_scenario,
    simulator_create_from_template,
    simulator_delete_connector,
    simulator_get_connector,
    simulator_get_report,
    simulator_get_status,
    simulator_list_connectors,
    simulator_list_templates,
    simulator_purge_scenario,
    simulator_pause_scenario,
    simulator_replay_scenario,
    simulator_resume_scenario,
    simulator_run_scenario,
)
from app.schemas import (
    SimulatorConnectorConfigureRequest,
    SimulatorRunResponse,
    SimulatorScenarioRequest,
    SimulatorScenarioStateResponse,
    SimulatorScenarioStatus,
    SimulatorTemplateCreateRequest,
)

router = APIRouter(prefix="/simulator", tags=["simulator"])


def _detail_from_http_error(error: httpx.HTTPStatusError) -> str:
    try:
        payload = error.response.json()
        if isinstance(payload, dict):
            detail = payload.get("detail")
            if isinstance(detail, str):
                return detail
            if detail is not None:
                return str(detail)
    except ValueError:
        pass
    return error.response.text or "Upstream simulator request failed"


def _rethrow_upstream_http_error(error: httpx.HTTPStatusError) -> None:
    raise HTTPException(
        status_code=error.response.status_code,
        detail=_detail_from_http_error(error),
    ) from error


@router.post("/scenarios", response_model=SimulatorScenarioStatus)
async def create_scenario(payload: SimulatorScenarioRequest) -> SimulatorScenarioStatus:
    try:
        response = await simulator_create_scenario(payload.scenario)
        return SimulatorScenarioStatus(**response)
    except httpx.HTTPStatusError as error:
        _rethrow_upstream_http_error(error)


@router.get("/scenarios/templates")
async def list_templates() -> dict:
    try:
        return await simulator_list_templates()
    except httpx.HTTPStatusError as error:
        _rethrow_upstream_http_error(error)


@router.post("/scenarios/templates/{template_id}", response_model=SimulatorScenarioStatus)
async def create_from_template(
    template_id: str,
    payload: SimulatorTemplateCreateRequest,
) -> SimulatorScenarioStatus:
    try:
        response = await simulator_create_from_template(
            template_id=template_id,
            tenant_id=payload.tenant_id,
            scenario_id=payload.scenario_id,
            connector_type=payload.connector_type,
        )
        return SimulatorScenarioStatus(**response)
    except httpx.HTTPStatusError as error:
        _rethrow_upstream_http_error(error)


@router.post("/scenarios/{scenario_id}/run", response_model=SimulatorRunResponse)
async def run_scenario(scenario_id: str) -> SimulatorRunResponse:
    try:
        response = await simulator_run_scenario(scenario_id)
        return SimulatorRunResponse(**response)
    except httpx.HTTPStatusError as error:
        _rethrow_upstream_http_error(error)


@router.post("/scenarios/{scenario_id}/replay", response_model=SimulatorRunResponse)
async def replay_scenario(scenario_id: str) -> SimulatorRunResponse:
    try:
        response = await simulator_replay_scenario(scenario_id)
        return SimulatorRunResponse(**response)
    except httpx.HTTPStatusError as error:
        _rethrow_upstream_http_error(error)


@router.post("/scenarios/{scenario_id}/pause", response_model=SimulatorScenarioStatus)
async def pause_scenario(scenario_id: str) -> SimulatorScenarioStatus:
    try:
        response = await simulator_pause_scenario(scenario_id)
        return SimulatorScenarioStatus(**response)
    except httpx.HTTPStatusError as error:
        _rethrow_upstream_http_error(error)


@router.post("/scenarios/{scenario_id}/resume", response_model=SimulatorScenarioStatus)
async def resume_scenario(scenario_id: str) -> SimulatorScenarioStatus:
    try:
        response = await simulator_resume_scenario(scenario_id)
        return SimulatorScenarioStatus(**response)
    except httpx.HTTPStatusError as error:
        _rethrow_upstream_http_error(error)


@router.get("/scenarios/{scenario_id}/status", response_model=SimulatorScenarioStateResponse)
async def get_status(scenario_id: str) -> SimulatorScenarioStateResponse:
    try:
        response = await simulator_get_status(scenario_id)
        return SimulatorScenarioStateResponse(**response)
    except httpx.HTTPStatusError as error:
        _rethrow_upstream_http_error(error)


@router.get("/scenarios/{scenario_id}/report")
async def get_report(scenario_id: str) -> dict:
    try:
        return await simulator_get_report(scenario_id)
    except httpx.HTTPStatusError as error:
        _rethrow_upstream_http_error(error)


@router.delete("/scenarios/{scenario_id}/purge", response_model=SimulatorScenarioStatus)
async def purge_scenario(scenario_id: str) -> SimulatorScenarioStatus:
    try:
        response = await simulator_purge_scenario(scenario_id)
        return SimulatorScenarioStatus(**response)
    except httpx.HTTPStatusError as error:
        _rethrow_upstream_http_error(error)


@router.get("/connectors")
async def list_connectors() -> dict:
    try:
        return await simulator_list_connectors()
    except httpx.HTTPStatusError as error:
        _rethrow_upstream_http_error(error)


@router.post("/connectors/configure")
async def configure_connector(payload: SimulatorConnectorConfigureRequest) -> dict:
    try:
        return await simulator_configure_connector(payload.connector)
    except httpx.HTTPStatusError as error:
        _rethrow_upstream_http_error(error)


@router.get("/connectors/{tenant_id}")
async def get_connector(tenant_id: str) -> dict:
    try:
        return await simulator_get_connector(tenant_id)
    except httpx.HTTPStatusError as error:
        _rethrow_upstream_http_error(error)


@router.delete("/connectors/{tenant_id}")
async def delete_connector(tenant_id: str) -> dict:
    try:
        return await simulator_delete_connector(tenant_id)
    except httpx.HTTPStatusError as error:
        _rethrow_upstream_http_error(error)
