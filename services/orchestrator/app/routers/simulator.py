from fastapi import APIRouter

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


@router.post("/scenarios", response_model=SimulatorScenarioStatus)
async def create_scenario(payload: SimulatorScenarioRequest) -> SimulatorScenarioStatus:
    response = await simulator_create_scenario(payload.scenario)
    return SimulatorScenarioStatus(**response)


@router.get("/scenarios/templates")
async def list_templates() -> dict:
    return await simulator_list_templates()


@router.post("/scenarios/templates/{template_id}", response_model=SimulatorScenarioStatus)
async def create_from_template(
    template_id: str,
    payload: SimulatorTemplateCreateRequest,
) -> SimulatorScenarioStatus:
    response = await simulator_create_from_template(
        template_id=template_id,
        tenant_id=payload.tenant_id,
        scenario_id=payload.scenario_id,
        connector_type=payload.connector_type,
    )
    return SimulatorScenarioStatus(**response)


@router.post("/scenarios/{scenario_id}/run", response_model=SimulatorRunResponse)
async def run_scenario(scenario_id: str) -> SimulatorRunResponse:
    response = await simulator_run_scenario(scenario_id)
    return SimulatorRunResponse(**response)


@router.post("/scenarios/{scenario_id}/replay", response_model=SimulatorRunResponse)
async def replay_scenario(scenario_id: str) -> SimulatorRunResponse:
    response = await simulator_replay_scenario(scenario_id)
    return SimulatorRunResponse(**response)


@router.post("/scenarios/{scenario_id}/pause", response_model=SimulatorScenarioStatus)
async def pause_scenario(scenario_id: str) -> SimulatorScenarioStatus:
    response = await simulator_pause_scenario(scenario_id)
    return SimulatorScenarioStatus(**response)


@router.post("/scenarios/{scenario_id}/resume", response_model=SimulatorScenarioStatus)
async def resume_scenario(scenario_id: str) -> SimulatorScenarioStatus:
    response = await simulator_resume_scenario(scenario_id)
    return SimulatorScenarioStatus(**response)


@router.get("/scenarios/{scenario_id}/status", response_model=SimulatorScenarioStateResponse)
async def get_status(scenario_id: str) -> SimulatorScenarioStateResponse:
    response = await simulator_get_status(scenario_id)
    return SimulatorScenarioStateResponse(**response)


@router.get("/scenarios/{scenario_id}/report")
async def get_report(scenario_id: str) -> dict:
    return await simulator_get_report(scenario_id)


@router.delete("/scenarios/{scenario_id}/purge", response_model=SimulatorScenarioStatus)
async def purge_scenario(scenario_id: str) -> SimulatorScenarioStatus:
    response = await simulator_purge_scenario(scenario_id)
    return SimulatorScenarioStatus(**response)


@router.get("/connectors")
async def list_connectors() -> dict:
    return await simulator_list_connectors()


@router.post("/connectors/configure")
async def configure_connector(payload: SimulatorConnectorConfigureRequest) -> dict:
    return await simulator_configure_connector(payload.connector)


@router.get("/connectors/{tenant_id}")
async def get_connector(tenant_id: str) -> dict:
    return await simulator_get_connector(tenant_id)


@router.delete("/connectors/{tenant_id}")
async def delete_connector(tenant_id: str) -> dict:
    return await simulator_delete_connector(tenant_id)
