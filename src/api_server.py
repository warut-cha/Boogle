from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

ROOT_DIR = Path(__file__).resolve().parent.parent
CONTRACTS_DIR = ROOT_DIR / "contracts"

findings_store: list[dict[str, Any]] = []
incidents_store: list[dict[str, Any]] = []
bob_analysis_store: dict[str, Any] | None = None
updates_store: list[dict[str, Any]] = []

app = FastAPI(title="Jeff API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_WS_ORIGINS = {
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
}


class WebSocketManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> bool:
        origin = websocket.headers.get("origin")

        if origin is not None and origin not in ALLOWED_WS_ORIGINS:
            await websocket.close(code=1008)
            return False

        await websocket.accept()
        self.active_connections.append(websocket)
        return True

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        disconnected: list[WebSocket] = []

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        for connection in disconnected:
            self.disconnect(connection)


ws_manager = WebSocketManager()


def load_json_file(path: Path, fallback: Any) -> Any:
    try:
        if not path.exists():
            return fallback

        with path.open("r", encoding="utf-8") as file:
            content = file.read().strip()

        if not content:
            return fallback

        return json.loads(content)
    except Exception:
        return fallback


def load_sample_findings() -> list[dict[str, Any]]:
    data = load_json_file(CONTRACTS_DIR / "sample_findings.json", [])
    return data if isinstance(data, list) else []


def load_sample_incident() -> dict[str, Any] | None:
    data = load_json_file(CONTRACTS_DIR / "sample_incident.json", None)
    return data if isinstance(data, dict) else None


def load_sample_bob_output() -> dict[str, Any]:
    data = load_json_file(CONTRACTS_DIR / "sample_bob_output.json", {})
    return data if isinstance(data, dict) else {}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    connected = await ws_manager.connect(websocket)

    if not connected:
        return

    try:
        while True:
            message = await websocket.receive_text()

            try:
                data = json.loads(message)
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except Exception:
                pass

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

    except Exception:
        ws_manager.disconnect(websocket)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "Jeff API",
    }


@app.get("/api/findings")
def get_findings() -> list[dict[str, Any]]:
    return findings_store


@app.get("/api/incidents")
def get_incidents() -> list[dict[str, Any]]:
    return incidents_store


@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id: str) -> dict[str, Any]:
    for incident in incidents_store:
        if incident.get("incident_id") == incident_id:
            return incident

    return {
        "incident_id": incident_id,
        "title": "Incident not found",
        "severity": "info",
        "severity_level": 1,
        "confidence_score": 0,
        "confidence_reasons": [],
        "confidence_limitations": [],
        "affected_repos": [],
        "affected_files": [],
        "affected_endpoints": [],
        "affected_database_tables": [],
        "findings": [],
        "attack_path": {"nodes": [], "edges": []},
        "related_memory": [],
    }


@app.get("/api/incidents/{incident_id}/bob-analysis")
def get_bob_analysis(incident_id: str) -> dict[str, Any]:
    return bob_analysis_store or load_sample_bob_output()


@app.post("/api/incidents/{incident_id}/analyze-with-bob")
async def analyze_with_bob(incident_id: str) -> dict[str, Any]:
    global bob_analysis_store

    bob_analysis_store = load_sample_bob_output()

    await ws_manager.broadcast(
        {
            "type": "bob_analysis",
            "incident_id": incident_id,
            "analysis": bob_analysis_store,
        }
    )

    return bob_analysis_store


@app.get("/api/updates")
def get_updates(since: str | None = None) -> dict[str, Any]:
    return {
        "findings": [],
        "incidents": [],
        "hasUpdates": False,
    }

def prepare_scan_result() -> tuple[str, list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    run_id = f"RUN-{uuid4().hex[:8]}"
    timestamp = datetime.now(timezone.utc).isoformat()

    sample_incident = load_sample_incident()
    sample_findings = load_sample_findings()
    sample_bob_output = load_sample_bob_output()

    new_findings: list[dict[str, Any]] = []

    for index, finding in enumerate(deepcopy(sample_findings), start=1):
        finding["finding_id"] = f"{run_id}-FIND-{index:03d}"
        finding["run_id"] = run_id
        finding["timestamp"] = timestamp
        new_findings.append(finding)

    new_incidents: list[dict[str, Any]] = []

    if sample_incident:
        incident = deepcopy(sample_incident)
        incident["incident_id"] = f"{run_id}-INC-001"
        incident["run_id"] = run_id
        incident["timestamp"] = timestamp

        if not incident.get("findings"):
            incident["findings"] = new_findings
        else:
            normalized_incident_findings = []
            for index, finding in enumerate(incident["findings"], start=1):
                finding["finding_id"] = f"{run_id}-INC-FIND-{index:03d}"
                finding["run_id"] = run_id
                finding["timestamp"] = timestamp
                normalized_incident_findings.append(finding)

            incident["findings"] = normalized_incident_findings

        new_incidents.append(incident)

    return run_id, new_findings, new_incidents, sample_bob_output

@app.post("/api/scan")
async def run_scan(payload: dict[str, Any]) -> dict[str, Any]:
    global bob_analysis_store

    run_id, new_findings, new_incidents, new_bob_output = prepare_scan_result()

    findings_store.extend(new_findings)
    incidents_store.extend(new_incidents)
    bob_analysis_store = new_bob_output

    message = {
        "type": "scan_completed",
        "run_id": run_id,
        "findings": new_findings,
        "incidents": new_incidents,
        "bob_analysis": bob_analysis_store,
    }

    await ws_manager.broadcast(message)

    return {
        "status": "success",
        "message": "Mock security scan completed",
        "run_id": run_id,
        "paths": payload.get("paths", []),
        "new_findings": new_findings,
        "new_incidents": new_incidents,
        "bob_analysis": bob_analysis_store,
        "total_findings": len(findings_store),
        "total_incidents": len(incidents_store),
    }


@app.delete("/api/reset")
async def reset_dashboard_data() -> dict[str, str]:
    global bob_analysis_store

    findings_store.clear()
    incidents_store.clear()
    updates_store.clear()
    bob_analysis_store = None

    await ws_manager.broadcast(
        {
            "type": "reset",
            "findings": [],
            "incidents": [],
            "bob_analysis": None,
        }
    )

    return {
        "status": "success",
        "message": "All stored dashboard data cleared",
    }