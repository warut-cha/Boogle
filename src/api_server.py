from __future__ import annotations

import json
from pathlib import Path
from typing import Any
try:
    from ai_engine.bob_client import BobClient
except ImportError:
    from src.ai_engine.bob_client import BobClient
try:
    from ai_engine.ai_memory_store import AIMemoryStore
except ImportError:
    from src.ai_engine.ai_memory_store import AIMemoryStore
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from uuid import uuid4
import asyncio

ROOT_DIR = Path(__file__).resolve().parent.parent
CONTRACTS_DIR = ROOT_DIR / "contracts"

findings_store: list[dict[str, Any]] = []
incidents_store: list[dict[str, Any]] = []
bob_analysis_store: dict[str, Any] | None = None
updates_store: list[dict[str, Any]] = []

app = FastAPI(title="JeffAPI")
bob_client = BobClient()
ai_memory_store = AIMemoryStore()
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

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
def attach_related_memory(incident: dict[str, Any]) -> list[dict[str, Any]]:
    related_memory = ai_memory_store.find_related_memories(
        incident=incident,
        limit=5,
    )

    incident["related_memory"] = related_memory

    return related_memory

async def run_bob_reasoning_background(incident: dict[str, Any]) -> None:
    """
    Run IBM Bob reasoning in the background so /api/attack-event
    can return immediately to the attack simulator.
    """
    incident_id = incident.get("incident_id", "INC-UNKNOWN")

    try:
        analysis = await asyncio.to_thread(
            run_bob_reasoning_for_incident,
            incident,
        )

    except Exception as error:
        analysis = {
            "attack_type": "IBM Bob analysis failed",
            "target": "Unknown",
            "severity": str(incident.get("severity", "medium")).lower(),
            "confidence_assessment": f"IBM Bob background analysis failed: {error}",
            "recommended_fixes": [
                {
                    "type": "config_fix",
                    "description": "Check watsonx.ai credentials, model ID, project ID, and backend logs.",
                }
            ],
            "generated_security_tests": [],
            "incident_report": (
                "## IBM Bob Analysis Failed\n\n"
                f"Incident `{incident_id}` was detected, but background Bob analysis failed.\n\n"
                f"Reason: {error}"
            ),
            "ai_memory": {
                "memory_type": "security_prevention_rule",
                "incident_pattern": "bob_background_analysis_failed",
                "root_cause": str(error),
                "signals_to_watch": [],
                "prevention_rule": "Fix Bob/watsonx configuration before relying on automated reasoning.",
                "recommended_tests": [],
                "severity_escalation_conditions": [],
            },
            "pr_draft": {
                "branch_name": "security/fix-bob-background-analysis",
                "pr_title": "Fix IBM Bob background analysis",
                "pr_description": "IBM Bob failed during background incident analysis.",
                "files_to_change": ["src/api_server.py", "src/ai_engine/bob_client.py"],
            },
            "memory_saved": False,
            "saved_memory_id": None,
        }

    await ws_manager.broadcast(
        {
            "type": "bob_analysis",
            "incident_id": incident_id,
            "analysis": analysis,
        }
    )

    await ws_manager.broadcast(
        {
            "type": "memory_updated",
            "memories": ai_memory_store.list_memories(),
            "count": len(ai_memory_store.list_memories()),
        }
    )

def run_bob_reasoning_for_incident(
    incident: dict[str, Any],
) -> dict[str, Any]:
    global bob_analysis_store

    related_memory = ai_memory_store.find_related_memories(
        incident=incident,
        limit=5,
    )

    incident["related_memory"] = related_memory

    bob_analysis_store = bob_client.analyze_incident(
        incident=incident,
        related_memory=related_memory,
    )

    saved_memory = ai_memory_store.save_from_bob_output(
        bob_output=bob_analysis_store,
        incident=incident,
    )

    if saved_memory:
        bob_analysis_store["memory_saved"] = True
        bob_analysis_store["saved_memory_id"] = saved_memory.get("memory_id")
    else:
        bob_analysis_store["memory_saved"] = False
        bob_analysis_store["saved_memory_id"] = None

    # Save the incident again because related_memory was attached.
    upsert_incident(incident)

    return bob_analysis_store

def build_finding_from_attack_event(event: dict[str, Any]) -> dict[str, Any]:
    endpoint = event.get("endpoint", "/api/v1/export-users")
    source_ip = event.get("source_ip", "unknown")
    event_type = event.get("event_type", "runtime_attack_event")

    return {
        "finding_id": f"FIND-{uuid4().hex[:8]}",
        "repo_name": event.get("repo_name", "legacy-backend"),
        "finding_type": "runtime_anomaly",
        "category": "runtime_behavior",
        "severity_hint": "critical",
        "source": "python_analyzer",
        "file": event.get("file", "runtime/api_gateway"),
        "line": None,
        "endpoint": endpoint,
        "database_table": event.get("database_table", "users"),
        "evidence": (
            f"Suspicious event {event_type} on endpoint {endpoint} "
            f"from source IP {source_ip}"
        ),
        "masked_value": None,
        "timestamp": utc_now(),

        # Important for AI memory and Bob context
        "event_type": event_type,
        "action": event.get("action"),
        "status": event.get("status"),
        "source_ip": source_ip,
        "rows_returned": event.get("rows_returned"),
        "query": event.get("query"),
        "metadata": event.get("metadata", {}),
    }


def build_incident_from_attack_event(
    event: dict[str, Any],
    finding: dict[str, Any],
) -> dict[str, Any]:
    endpoint = finding.get("endpoint", "/api/v1/export-users")

    return {
        "incident_id": f"INC-{uuid4().hex[:8]}",
        "title": "Real-time attack detected against abandoned export API",
        "severity": "critical",
        "severity_level": 5,
        "confidence_score": 0.92,
        "confidence_reasons": [
            "Attack simulator triggered suspicious access pattern",
            "Deprecated export endpoint was targeted",
            "Sensitive users table may be affected",
            "Runtime attack signal was received in real time",
        ],
        "confidence_limitations": [
            "This is a simulated attack event, not confirmed external exfiltration",
        ],
        "affected_repos": [event.get("repo_name", "legacy-backend")],
        "affected_files": [event.get("file", "runtime/api_gateway")],
        "affected_endpoints": [endpoint],
        "affected_database_tables": [event.get("database_table", "users")],
        "findings": [finding],
        "attack_path": {
            "nodes": [
                {
                    "id": "attacker",
                    "label": "Attack Simulator",
                    "type": "runtime",
                },
                {
                    "id": "old_api",
                    "label": "Abandoned Export API",
                    "type": "api",
                },
                {
                    "id": "db",
                    "label": "Users Table",
                    "type": "database",
                },
                {
                    "id": "impact",
                    "label": "Possible Data Exposure",
                    "type": "impact",
                },
            ],
            "edges": [
                {
                    "from": "attacker",
                    "to": "old_api",
                    "label": "targets",
                },
                {
                    "from": "old_api",
                    "to": "db",
                    "label": "may access",
                },
                {
                    "from": "db",
                    "to": "impact",
                    "label": "may expose",
                },
            ],
        },
        "related_memory": [],
        "timestamp": utc_now(),
    }


def upsert_incident(incident: dict[str, Any]) -> None:
    incident_id = incident.get("incident_id")

    for index, existing in enumerate(incidents_store):
        if existing.get("incident_id") == incident_id:
            incidents_store[index] = incident
            return

    incidents_store.append(incident)


def upsert_finding(finding: dict[str, Any]) -> None:
    finding_id = finding.get("finding_id")

    for index, existing in enumerate(findings_store):
        if existing.get("finding_id") == finding_id:
            findings_store[index] = finding
            return

    findings_store.append(finding)

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


def upsert_incident(incident: dict[str, Any]) -> None:
    incident_id = incident.get("incident_id")

    for index, existing in enumerate(incidents_store):
        if existing.get("incident_id") == incident_id:
            incidents_store[index] = incident
            return

    incidents_store.append(incident)


def upsert_findings(findings: list[dict[str, Any]]) -> None:
    existing_ids = {
        finding.get("finding_id")
        for finding in findings_store
        if finding.get("finding_id")
    }

    for finding in findings:
        finding_id = finding.get("finding_id")

        if finding_id and finding_id in existing_ids:
            continue

        findings_store.append(finding)

        if finding_id:
            existing_ids.add(finding_id)


async def publish_detected_incident(incident: dict[str, Any]) -> None:
    """
    Use this whenever an attack/new incident is detected outside manual scan.
    This version supports AI memory.
    """
    incident_id = incident.get("incident_id", "INC-UNKNOWN")
    incident_findings = incident.get("findings", [])

    if not isinstance(incident_findings, list):
        incident_findings = []

    attach_related_memory(incident)

    upsert_incident(incident)
    upsert_findings(incident_findings)

    await ws_manager.broadcast(
        {
            "type": "attack_detected",
            "incident": incident,
            "findings": incident_findings,
            "bob_analysis": None,
            "bob_status": "running",
        }
    )

    asyncio.create_task(run_bob_reasoning_background(incident))


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
        "service": "Bob Sentinel API",
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
    if bob_analysis_store is None:
        return {}

    return bob_analysis_store


@app.post("/api/incidents/{incident_id}/analyze-with-bob")
async def analyze_with_bob(incident_id: str) -> dict[str, Any]:
    incident = None

    for existing in incidents_store:
        if existing.get("incident_id") == incident_id:
            incident = existing
            break

    if incident is None:
        incident = {
            "incident_id": incident_id,
            "title": "Unknown incident",
            "severity": "medium",
            "severity_level": 3,
            "confidence_score": 0.5,
            "confidence_reasons": [
                "Incident was requested for IBM Bob analysis."
            ],
            "confidence_limitations": [
                "Incident details were not found in backend memory."
            ],
            "affected_repos": [],
            "affected_files": [],
            "affected_endpoints": [],
            "affected_database_tables": [],
            "findings": [],
            "attack_path": {"nodes": [], "edges": []},
            "related_memory": [],
        }

    analysis = run_bob_reasoning_for_incident(incident)

    await ws_manager.broadcast(
        {
            "type": "bob_analysis",
            "incident_id": incident_id,
            "analysis": analysis,
        }
    )

    return analysis

@app.get("/api/updates")
def get_updates(since: str | None = None) -> dict[str, Any]:
    return {
        "findings": [],
        "incidents": [],
        "hasUpdates": False,
    }


@app.post("/api/scan")
async def run_scan(payload: dict[str, Any]) -> dict[str, Any]:
    global findings_store, incidents_store, bob_analysis_store

    sample_incident = load_sample_incident()
    sample_findings = load_sample_findings()

    latest_incident: dict[str, Any] | None = None

    if sample_incident:
        incident_findings = sample_incident.get("findings")

        if isinstance(incident_findings, list) and len(incident_findings) > 0:
            sample_findings = incident_findings

        # Save incident and findings
        upsert_incident(sample_incident)
        upsert_findings(sample_findings)

        latest_incident = sample_incident

    else:
        # No incident, only findings
        upsert_findings(sample_findings)

        if incidents_store:
            latest_incident = incidents_store[-1]

    if latest_incident:
        # This version supports AI memory:
        # 1. retrieve related memory
        # 2. send incident + memory to Bob
        # 3. save Bob's new ai_memory
        bob_analysis_store = run_bob_reasoning_for_incident(latest_incident)
    else:
        bob_analysis_store = {
            "attack_type": "IBM Bob analysis unavailable",
            "target": "No incident available for analysis",
            "severity": "info",
            "confidence_assessment": "No incident was available to send to IBM Bob.",
            "recommended_fixes": [],
            "generated_security_tests": [],
            "incident_report": "## No IBM Bob Analysis\n\nNo incident was available.",
            "ai_memory": {
                "memory_type": "security_prevention_rule",
                "incident_pattern": "no_incident_available",
                "root_cause": "No incident was available for IBM Bob analysis.",
                "signals_to_watch": [],
                "prevention_rule": "Run detection before requesting Bob analysis.",
                "recommended_tests": [],
                "severity_escalation_conditions": [],
            },
            "pr_draft": {
                "branch_name": "security/no-incident",
                "pr_title": "No incident available",
                "pr_description": "No incident was available for IBM Bob analysis.",
                "files_to_change": [],
            },
            "memory_saved": False,
        }

    await ws_manager.broadcast(
        {
            "type": "scan_completed",
            "findings": findings_store,
            "incidents": incidents_store,
            "bob_analysis": bob_analysis_store,
        }
    )

    return {
        "status": "success",
        "message": "Mock security scan completed",
        "paths": payload.get("paths", []),
        "findings_count": len(findings_store),
        "incidents_count": len(incidents_store),
        "bob_status": bob_analysis_store.get("attack_type"),
        "memory_saved": bob_analysis_store.get("memory_saved", False),
        "saved_memory_id": bob_analysis_store.get("saved_memory_id"),
    }

@app.post("/api/simulate-attack")
async def simulate_attack() -> dict[str, Any]:
    sample_incident = load_sample_incident()

    if not sample_incident:
        sample_incident = {
            "incident_id": "INC-SIMULATED",
            "title": "Simulated attack detected",
            "severity": "critical",
            "severity_level": 5,
            "confidence_score": 0.9,
            "confidence_reasons": ["Simulated attack event"],
            "confidence_limitations": [],
            "affected_repos": ["legacy-backend"],
            "affected_files": [],
            "affected_endpoints": ["/api/v1/export-users"],
            "affected_database_tables": ["users"],
            "findings": [],
            "attack_path": {"nodes": [], "edges": []},
            "related_memory": [],
        }

    await publish_detected_incident(sample_incident)

    return {
        "status": "success",
        "message": "Simulated attack published",
        "incident_id": sample_incident.get("incident_id"),
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
        "message": "Dashboard data cleared. AI memory was kept.",
    }

@app.post("/api/attack-event")
async def ingest_attack_event(event: dict[str, Any]) -> dict[str, Any]:
    finding = build_finding_from_attack_event(event)
    incident = build_incident_from_attack_event(event, finding)

    attach_related_memory(incident)

    upsert_finding(finding)
    upsert_incident(incident)

    await ws_manager.broadcast(
        {
            "type": "attack_detected",
            "finding": finding,
            "findings": [finding],
            "incident": incident,
            "bob_analysis": None,
            "bob_status": "running",
        }
    )

    asyncio.create_task(run_bob_reasoning_background(incident))

    return {
        "status": "accepted",
        "message": "Attack event ingested. IBM Bob reasoning is running in the background.",
        "finding_id": finding["finding_id"],
        "incident_id": incident["incident_id"],
        "bob_status": "running",
        "related_memory_count": len(incident.get("related_memory", [])),
    }

@app.get("/api/memory")
def get_ai_memory() -> dict[str, Any]:
    memories = ai_memory_store.list_memories()

    return {
        "count": len(memories),
        "memories": memories,
    }


@app.delete("/api/memory")
def clear_ai_memory() -> dict[str, Any]:
    ai_memory_store.clear()

    return {
        "status": "success",
        "message": "AI memory cleared",
    }