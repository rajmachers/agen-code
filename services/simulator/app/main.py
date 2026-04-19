from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from os import getenv
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from jsonschema import ValidationError, validate
from pydantic import BaseModel, Field

app = FastAPI(
    title="Simulator Service",
    description="Scenario-driven synthetic data simulator for demos, QA, and analytics validation.",
    version="0.1.0",
)

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_DIR = BASE_DIR / "schemas"


def _load_schema(filename: str) -> dict[str, Any]:
    with (SCHEMA_DIR / filename).open("r", encoding="utf-8") as handle:
        return json.load(handle)


SCENARIO_SCHEMA = _load_schema("simulator-scenario-schema.json")
CONNECTOR_SCHEMA = _load_schema("connector-config-schema.json")


class ScenarioEnvelope(BaseModel):
    payload: dict[str, Any]
    actor_id: str | None = None
    request_id: str | None = None
    simulation_source: str | None = None


class ConnectorEnvelope(BaseModel):
    payload: dict[str, Any]
    actor_id: str | None = None
    request_id: str | None = None
    simulation_source: str | None = None


class ScenarioState(BaseModel):
    scenario_id: str
    status: str
    created_at: str
    updated_at: str
    run_count: int = 0
    last_report: dict[str, Any] = Field(default_factory=dict)
    actor_id: str | None = None
    request_id: str | None = None
    simulation_source: str | None = None


SCENARIO_TEMPLATES: dict[str, dict[str, Any]] = {
    "quick_demo": {
        "scenarioType": "quick_demo",
        "seed": 12345,
        "courseConfig": {"courseCount": 2, "pedagogyProfile": "foundational"},
        "batchConfig": {
            "batchCount": 1,
            "modeMix": {"practice": 0.8, "interview": 0.1, "exam": 0.1},
        },
        "population": {"candidates": 40, "instructors": 2, "evaluators": 2},
        "timeline": {"mode": "accelerated", "durationDays": 14},
        "governance": {"simulationSource": "simulator_service", "purgeOnComplete": False},
    },
    "academic_cohort": {
        "scenarioType": "academic_cohort",
        "seed": 98765,
        "courseConfig": {"courseCount": 4, "pedagogyProfile": "mixed"},
        "batchConfig": {
            "batchCount": 2,
            "modeMix": {"practice": 0.7, "interview": 0.1, "exam": 0.2},
        },
        "population": {"candidates": 120, "instructors": 4, "evaluators": 4},
        "timeline": {"mode": "realtime", "durationDays": 90},
        "governance": {"simulationSource": "simulator_service", "purgeOnComplete": False},
    },
}


DB_PATH = getenv("SIMULATOR_DB_PATH", "/tmp/simulator.db")


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _validate_payload(payload: dict[str, Any], schema: dict[str, Any], kind: str) -> None:
    try:
        validate(instance=payload, schema=schema)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid {kind} payload: {exc.message}") from exc


def _conn() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _init_db() -> None:
    with _conn() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS connectors (
                tenant_id TEXT PRIMARY KEY,
                payload_json TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                actor_id TEXT,
                request_id TEXT,
                simulation_source TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS scenarios (
                scenario_id TEXT PRIMARY KEY,
                payload_json TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                run_count INTEGER NOT NULL DEFAULT 0,
                last_report_json TEXT NOT NULL DEFAULT '{}',
                actor_id TEXT,
                request_id TEXT,
                simulation_source TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS run_reports (
                scenario_id TEXT PRIMARY KEY,
                report_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        _ensure_column(connection, "connectors", "actor_id", "TEXT")
        _ensure_column(connection, "connectors", "request_id", "TEXT")
        _ensure_column(connection, "connectors", "simulation_source", "TEXT")
        _ensure_column(connection, "scenarios", "actor_id", "TEXT")
        _ensure_column(connection, "scenarios", "request_id", "TEXT")
        _ensure_column(connection, "scenarios", "simulation_source", "TEXT")


def _ensure_column(connection: sqlite3.Connection, table: str, column: str, col_type: str) -> None:
    existing_columns = {
        row["name"] for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
    }
    if column not in existing_columns:
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")


@app.on_event("startup")
def startup() -> None:
    _init_db()


def _get_scenario_row(scenario_id: str) -> sqlite3.Row:
    with _conn() as connection:
        row = connection.execute(
            "SELECT * FROM scenarios WHERE scenario_id = ?",
            (scenario_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return row


def _create_scenario_record(
    payload: dict[str, Any],
    actor_id: str | None = None,
    request_id: str | None = None,
    simulation_source: str | None = None,
) -> dict[str, Any]:
    _validate_payload(payload, SCENARIO_SCHEMA, "scenario")
    scenario_id = payload["scenarioId"]
    now = _utc_now()
    effective_source = simulation_source or payload.get("governance", {}).get("simulationSource")
    with _conn() as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO scenarios (
                scenario_id,
                payload_json,
                status,
                created_at,
                updated_at,
                run_count,
                last_report_json,
                actor_id,
                request_id,
                simulation_source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                scenario_id,
                json.dumps(payload),
                "created",
                now,
                now,
                0,
                "{}",
                actor_id,
                request_id,
                effective_source,
            ),
        )
        connection.execute("DELETE FROM run_reports WHERE scenario_id = ?", (scenario_id,))
    return {
        "status": "created",
        "scenarioId": scenario_id,
        "actor_id": actor_id,
        "request_id": request_id,
        "simulation_source": effective_source,
    }


@app.get("/health")
def health() -> dict[str, Any]:
    with _conn() as connection:
        scenario_count = connection.execute("SELECT COUNT(1) FROM scenarios").fetchone()[0]
        connector_count = connection.execute("SELECT COUNT(1) FROM connectors").fetchone()[0]

    return {
        "status": "ok",
        "service": "simulator",
        "scenario_count": scenario_count,
        "connector_count": connector_count,
    }


@app.post("/sim/v1/connectors/configure")
def configure_connector(body: ConnectorEnvelope) -> dict[str, Any]:
    payload = body.payload
    _validate_payload(payload, CONNECTOR_SCHEMA, "connector config")

    tenant_id = payload["tenantId"]
    updated_at = _utc_now()
    effective_source = body.simulation_source or "simulator_service"
    with _conn() as connection:
        connection.execute(
            """
            INSERT INTO connectors (
                tenant_id,
                payload_json,
                updated_at,
                actor_id,
                request_id,
                simulation_source
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(tenant_id) DO UPDATE SET
                payload_json = excluded.payload_json,
                updated_at = excluded.updated_at,
                actor_id = excluded.actor_id,
                request_id = excluded.request_id,
                simulation_source = excluded.simulation_source
            """,
            (
                tenant_id,
                json.dumps(payload),
                updated_at,
                body.actor_id,
                body.request_id,
                effective_source,
            ),
        )
    return {
        "status": "configured",
        "tenantId": tenant_id,
        "connectorType": payload["connectorType"],
        "actor_id": body.actor_id,
        "request_id": body.request_id,
        "simulation_source": effective_source,
    }


@app.get("/sim/v1/connectors")
def list_connectors() -> dict[str, Any]:
    with _conn() as connection:
        rows = connection.execute(
            """
            SELECT tenant_id, payload_json, updated_at, actor_id, request_id, simulation_source
            FROM connectors
            ORDER BY tenant_id
            """
        ).fetchall()

    connectors = [
        {
            "tenantId": row["tenant_id"],
            "updatedAt": row["updated_at"],
            "connectorType": json.loads(row["payload_json"])["connectorType"],
            "actor_id": row["actor_id"],
            "request_id": row["request_id"],
            "simulation_source": row["simulation_source"],
        }
        for row in rows
    ]
    return {"items": connectors, "count": len(connectors)}


@app.get("/sim/v1/connectors/{tenant_id}")
def get_connector(tenant_id: str) -> dict[str, Any]:
    with _conn() as connection:
        row = connection.execute(
            """
            SELECT payload_json, updated_at, actor_id, request_id, simulation_source
            FROM connectors
            WHERE tenant_id = ?
            """,
            (tenant_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Connector not found")

    return {
        "tenantId": tenant_id,
        "updatedAt": row["updated_at"],
        "payload": json.loads(row["payload_json"]),
        "actor_id": row["actor_id"],
        "request_id": row["request_id"],
        "simulation_source": row["simulation_source"],
    }


@app.delete("/sim/v1/connectors/{tenant_id}")
def delete_connector(tenant_id: str) -> dict[str, Any]:
    with _conn() as connection:
        deleted = connection.execute(
            "DELETE FROM connectors WHERE tenant_id = ?",
            (tenant_id,),
        ).rowcount

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Connector not found")

    return {"status": "deleted", "tenantId": tenant_id, "deletedAt": _utc_now()}


@app.post("/sim/v1/scenarios/create")
def create_scenario(body: ScenarioEnvelope) -> dict[str, Any]:
    return _create_scenario_record(
        body.payload,
        actor_id=body.actor_id,
        request_id=body.request_id,
        simulation_source=body.simulation_source,
    )


@app.get("/sim/v1/scenarios/templates")
def list_templates() -> dict[str, Any]:
    items = [{"templateId": key, **value} for key, value in SCENARIO_TEMPLATES.items()]
    return {"items": items, "count": len(items)}


@app.post("/sim/v1/scenarios/templates/{template_id}/create")
def create_scenario_from_template(
    template_id: str,
    tenant_id: str,
    scenario_id: str,
    connector_type: str = "moodle",
    actor_id: str | None = None,
    request_id: str | None = None,
    simulation_source: str | None = None,
) -> dict[str, Any]:
    template = SCENARIO_TEMPLATES.get(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")

    payload = {
        "scenarioId": scenario_id,
        "tenantConfig": {"tenantId": tenant_id, "connectorType": connector_type},
        **template,
    }
    return _create_scenario_record(
        payload,
        actor_id=actor_id,
        request_id=request_id,
        simulation_source=simulation_source,
    )


@app.post("/sim/v1/scenarios/{scenario_id}/run")
def run_scenario(scenario_id: str) -> dict[str, Any]:
    row = _get_scenario_row(scenario_id)
    scenario = json.loads(row["payload_json"])
    run_count = int(row["run_count"]) + 1
    updated_at = _utc_now()
    simulation_source = row["simulation_source"] or scenario["governance"]["simulationSource"]

    report = {
        "scenarioId": scenario_id,
        "status": "completed",
        "coursesGenerated": scenario["courseConfig"]["courseCount"],
        "batchesGenerated": scenario["batchConfig"]["batchCount"],
        "candidatesGenerated": scenario["population"]["candidates"],
        "simulationSource": simulation_source,
        "simulation_source": simulation_source,
        "completedAt": updated_at,
    }
    with _conn() as connection:
        connection.execute(
            """
            UPDATE scenarios
            SET status = ?, updated_at = ?, run_count = ?, last_report_json = ?
            WHERE scenario_id = ?
            """,
            ("completed", updated_at, run_count, json.dumps(report), scenario_id),
        )
        connection.execute(
            """
            INSERT INTO run_reports (scenario_id, report_json, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(scenario_id) DO UPDATE SET
                report_json = excluded.report_json,
                updated_at = excluded.updated_at
            """,
            (scenario_id, json.dumps(report), updated_at),
        )

    return {
        "status": "run_completed",
        "report": report,
    }


@app.post("/sim/v1/scenarios/{scenario_id}/replay")
def replay_scenario(scenario_id: str) -> dict[str, Any]:
    _get_scenario_row(scenario_id)

    result = run_scenario(scenario_id)
    result["status"] = "replay_completed"
    return result


@app.post("/sim/v1/scenarios/{scenario_id}/pause")
def pause_scenario(scenario_id: str) -> dict[str, Any]:
    _get_scenario_row(scenario_id)
    with _conn() as connection:
        connection.execute(
            "UPDATE scenarios SET status = ?, updated_at = ? WHERE scenario_id = ?",
            ("paused", _utc_now(), scenario_id),
        )
    return {"status": "paused", "scenarioId": scenario_id}


@app.post("/sim/v1/scenarios/{scenario_id}/resume")
def resume_scenario(scenario_id: str) -> dict[str, Any]:
    _get_scenario_row(scenario_id)
    with _conn() as connection:
        connection.execute(
            "UPDATE scenarios SET status = ?, updated_at = ? WHERE scenario_id = ?",
            ("created", _utc_now(), scenario_id),
        )
    return {"status": "resumed", "scenarioId": scenario_id}


@app.get("/sim/v1/scenarios/{scenario_id}/status")
def scenario_status(scenario_id: str) -> dict[str, Any]:
    row = _get_scenario_row(scenario_id)
    return ScenarioState(
        scenario_id=row["scenario_id"],
        status=row["status"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        run_count=row["run_count"],
        last_report=json.loads(row["last_report_json"]),
        actor_id=row["actor_id"],
        request_id=row["request_id"],
        simulation_source=row["simulation_source"],
    ).model_dump()


@app.get("/sim/v1/scenarios/{scenario_id}/report")
def scenario_report(scenario_id: str) -> dict[str, Any]:
    with _conn() as connection:
        row = connection.execute(
            "SELECT report_json FROM run_reports WHERE scenario_id = ?",
            (scenario_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="No report available. Run scenario first.")
    return json.loads(row["report_json"])


@app.delete("/sim/v1/scenarios/{scenario_id}/purge")
def purge_scenario(scenario_id: str) -> dict[str, Any]:
    with _conn() as connection:
        deleted = connection.execute(
            "DELETE FROM scenarios WHERE scenario_id = ?",
            (scenario_id,),
        ).rowcount
        connection.execute(
            "DELETE FROM run_reports WHERE scenario_id = ?",
            (scenario_id,),
        )

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Scenario not found")

    return {
        "status": "purged",
        "scenarioId": scenario_id,
        "purgedAt": _utc_now(),
    }
