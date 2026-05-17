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
import os
import yaml
from uuid import uuid4

import os
import yaml
from uuid import uuid4

try:
    from scanners.rust_scanner_client import RustScannerClient
    from correlators.incident_correlator import IncidentCorrelator
    from classifiers.severity_classifier import SeverityClassifier
    from classifiers.confidence_scorer import ConfidenceScorer
    from correlators.attack_path_builder import AttackPathBuilder
except ImportError:
    from src.scanners.rust_scanner_client import RustScannerClient
    from src.correlators.incident_correlator import IncidentCorrelator
    from src.classifiers.severity_classifier import SeverityClassifier
    from src.classifiers.confidence_scorer import ConfidenceScorer
    from src.correlators.attack_path_builder import AttackPathBuilder

ROOT_DIR = Path(__file__).resolve().parent.parent
CONTRACTS_DIR = ROOT_DIR / "contracts"

findings_store: list[dict[str, Any]] = []
incidents_store: list[dict[str, Any]] = []
bob_analysis_store: dict[str, Any] | None = None
bob_analyses_store: list[dict[str, Any]] = []
updates_store: list[dict[str, Any]] = []

app = FastAPI(title="JeffAPI")
bob_client = BobClient()
ai_memory_store = AIMemoryStore()
def load_config() -> dict[str, Any]:
    config_path = ROOT_DIR / "config" / "config.yaml"

    if not config_path.exists():
        return {
            "analysis": {
                "correlation": {
                    "time_window_minutes": 120,
                    "min_confidence": 0.7,
                }
            },
            "severity": {},
        }

    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


CONFIG = load_config()

rust_scanner = RustScannerClient()

correlator = IncidentCorrelator(
    CONFIG.get("analysis", {}).get("correlation", {})
)

classifier = SeverityClassifier(
    CONFIG.get("severity", {})
)

confidence_scorer = ConfidenceScorer()

attack_path_builder = AttackPathBuilder()

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

def resolve_scan_paths(paths: list[str]) -> list[str]:
    """
    Resolve user-provided scan paths relative to the project root.

    This allows:
    - "." to scan the current repo
    - "./mock-repos"
    - "mock-repos/frontend-app"
    - absolute paths inside the project

    It blocks scanning outside the project root for safety.
    """
    if not paths:
        paths = ["."]

    project_root = ROOT_DIR.resolve()
    resolved_paths: list[str] = []

    for raw_path in paths:
        raw_path = str(raw_path).strip()

        if not raw_path:
            continue

        candidate = Path(raw_path).expanduser()

        if not candidate.is_absolute():
            candidate = project_root / candidate

        resolved = candidate.resolve()

        if not str(resolved).startswith(str(project_root)):
            raise ValueError(
                f"Scan path is outside the project root and was rejected: {raw_path}"
            )

        if not resolved.exists():
            raise ValueError(f"Scan path does not exist: {raw_path}")

        resolved_paths.append(str(resolved))

    if not resolved_paths:
        raise ValueError("No valid scan paths provided.")

    return resolved_paths

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
def severity_to_level(severity: str) -> int:
    severity = str(severity or "medium").lower()

    return {
        "info": 1,
        "low": 2,
        "medium": 3,
        "high": 4,
        "critical": 5,
    }.get(severity, 3)


def normalize_scanner_finding(finding: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize scanner output so it works with:
    - frontend Finding type
    - correlator
    - Bob prompt
    """
    normalized = dict(finding)

    finding_type = (
        normalized.get("finding_type")
        or normalized.get("type")
        or normalized.get("category")
        or "runtime_anomaly"
    )

    severity = (
        normalized.get("severity_hint")
        or normalized.get("severity")
        or "medium"
    )

    file_value = (
        normalized.get("file")
        or normalized.get("file_path")
        or normalized.get("path")
        or "unknown"
    )

    normalized["finding_id"] = normalized.get("finding_id") or f"FIND-{uuid4().hex[:8]}"
    normalized["repo_name"] = normalized.get("repo_name") or "scanned-repository"
    normalized["finding_type"] = str(finding_type)
    normalized["type"] = str(finding_type)
    normalized["category"] = normalized.get("category") or "unknown"
    normalized["severity_hint"] = str(severity).lower()
    normalized["severity"] = str(severity).lower()
    normalized["source"] = normalized.get("source") or "rust_scanner"
    normalized["file"] = str(file_value)
    normalized["file_path"] = str(file_value)
    normalized["line"] = normalized.get("line")
    normalized["endpoint"] = normalized.get("endpoint")
    normalized["database_table"] = normalized.get("database_table")
    normalized["evidence"] = (
        normalized.get("evidence")
        or normalized.get("description")
        or normalized.get("message")
        or f"{finding_type} detected in {file_value}"
    )
    normalized["description"] = normalized.get("description") or normalized["evidence"]
    normalized["masked_value"] = normalized.get("masked_value")
    normalized["timestamp"] = normalized.get("timestamp") or utc_now()

    return normalized


def build_fallback_incident_from_findings(
    findings: list[dict[str, Any]],
    scan_paths: list[str],
) -> dict[str, Any] | None:
    """
    If the correlator does not create an incident, create one from findings.
    This keeps Incident Analysis and Bob Analysis working for repo scans.
    """
    if not findings:
        return None

    severity_order = {
        "info": 1,
        "low": 2,
        "medium": 3,
        "high": 4,
        "critical": 5,
    }

    highest_severity = "medium"

    for finding in findings:
        severity = str(
            finding.get("severity_hint")
            or finding.get("severity")
            or "medium"
        ).lower()

        if severity_order.get(severity, 3) > severity_order.get(highest_severity, 3):
            highest_severity = severity

    affected_repos = sorted({
        str(finding.get("repo_name"))
        for finding in findings
        if finding.get("repo_name")
    })

    affected_files = sorted({
        str(finding.get("file"))
        for finding in findings
        if finding.get("file")
    })

    affected_endpoints = sorted({
        str(finding.get("endpoint"))
        for finding in findings
        if finding.get("endpoint")
    })

    affected_database_tables = sorted({
        str(finding.get("database_table"))
        for finding in findings
        if finding.get("database_table")
    })

    finding_types = sorted({
        str(finding.get("finding_type") or finding.get("type") or "unknown")
        for finding in findings
    })

    return {
        "incident_id": f"INC-{uuid4().hex[:8]}",
        "title": f"Repository scan detected {len(findings)} security finding(s)",
        "severity": highest_severity,
        "severity_level": severity_to_level(highest_severity),
        "confidence_score": 0.75,
        "confidence_reasons": [
            "Repository scanner detected one or more security findings.",
            f"Finding types: {', '.join(finding_types)}",
            f"Scanned paths: {', '.join(scan_paths)}",
        ],
        "confidence_limitations": [
            "This incident was created from scan findings because the correlator did not produce a grouped incident.",
        ],
        "affected_repos": affected_repos,
        "affected_files": affected_files,
        "affected_endpoints": affected_endpoints,
        "affected_database_tables": affected_database_tables,
        "findings": findings,
        "attack_path": {
            "nodes": [
                {
                    "id": "repo",
                    "label": "Scanned Repository",
                    "type": "infrastructure",
                },
                {
                    "id": "finding",
                    "label": "Security Finding",
                    "type": "runtime",
                },
                {
                    "id": "impact",
                    "label": "Potential Security Impact",
                    "type": "impact",
                },
            ],
            "edges": [
                {
                    "from": "repo",
                    "to": "finding",
                    "label": "contains",
                },
                {
                    "from": "finding",
                    "to": "impact",
                    "label": "may cause",
                },
            ],
        },
        "related_memory": [],
        "timestamp": utc_now(),
    }


def normalize_incident_for_frontend(incident: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize incident output so frontend, Bob, and memory all receive
    the same contract.
    """
    normalized = dict(incident)

    findings = normalized.get("findings", [])
    if not isinstance(findings, list):
        findings = []

    findings = [
        normalize_scanner_finding(finding)
        for finding in findings
        if isinstance(finding, dict)
    ]

    severity = normalized.get("severity", "medium")

    if isinstance(severity, dict):
        severity_level = severity.get("level", 3)
        severity = (
            severity.get("level_name")
            or severity.get("name")
            or severity.get("label")
            or "medium"
        )
    else:
        severity_level = normalized.get("severity_level", severity_to_level(str(severity)))

    severity = str(severity).lower()

    affected_repos = sorted({
        str(finding.get("repo_name"))
        for finding in findings
        if finding.get("repo_name")
    })

    affected_files = sorted({
        str(finding.get("file"))
        for finding in findings
        if finding.get("file")
    })

    affected_endpoints = sorted({
        str(finding.get("endpoint"))
        for finding in findings
        if finding.get("endpoint")
    })

    affected_database_tables = sorted({
        str(finding.get("database_table"))
        for finding in findings
        if finding.get("database_table")
    })

    return {
        "incident_id": normalized.get("incident_id") or f"INC-{uuid4().hex[:8]}",
        "title": normalized.get("title") or "Repository security incident detected",
        "severity": severity,
        "severity_level": int(severity_level),
        "confidence_score": normalized.get("confidence_score", 0.5),
        "confidence_reasons": normalized.get(
            "confidence_reasons",
            ["Repository scan produced correlated security evidence."],
        ),
        "confidence_limitations": normalized.get("confidence_limitations", []),
        "affected_repos": normalized.get("affected_repos") or affected_repos,
        "affected_files": normalized.get("affected_files") or affected_files,
        "affected_endpoints": normalized.get("affected_endpoints") or affected_endpoints,
        "affected_database_tables": (
            normalized.get("affected_database_tables")
            or affected_database_tables
        ),
        "findings": findings,
        "attack_path": normalized.get("attack_path") or {"nodes": [], "edges": []},
        "related_memory": normalized.get("related_memory") or [],
        "timestamp": normalized.get("timestamp") or utc_now(),
    }
def severity_to_level(severity: str) -> int:
    severity = str(severity or "medium").lower()

    return {
        "info": 1,
        "low": 2,
        "medium": 3,
        "high": 4,
        "critical": 5,
    }.get(severity, 3)


def normalize_scanner_finding(finding: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(finding)

    finding_type = (
        normalized.get("finding_type")
        or normalized.get("type")
        or normalized.get("category")
        or "runtime_anomaly"
    )

    severity = (
        normalized.get("severity_hint")
        or normalized.get("severity")
        or "medium"
    )

    file_value = (
        normalized.get("file")
        or normalized.get("file_path")
        or normalized.get("path")
        or "unknown"
    )

    evidence_value = (
        normalized.get("evidence")
        or normalized.get("description")
        or normalized.get("message")
        or f"{finding_type} detected in {file_value}"
    )

    normalized["finding_id"] = normalized.get("finding_id") or f"FIND-{uuid4().hex[:8]}"
    normalized["repo_name"] = normalized.get("repo_name") or "scanned-repository"
    normalized["finding_type"] = str(finding_type)
    normalized["type"] = str(finding_type)
    normalized["category"] = normalized.get("category") or "unknown"
    normalized["severity_hint"] = str(severity).lower()
    normalized["severity"] = str(severity).lower()
    normalized["source"] = normalized.get("source") or "rust_scanner"
    normalized["file"] = str(file_value)
    normalized["file_path"] = str(file_value)
    normalized["line"] = normalized.get("line")
    normalized["endpoint"] = normalized.get("endpoint")
    normalized["database_table"] = normalized.get("database_table")
    normalized["evidence"] = str(evidence_value)
    normalized["description"] = str(evidence_value)
    normalized["masked_value"] = normalized.get("masked_value")
    normalized["timestamp"] = normalized.get("timestamp") or utc_now()

    return normalized


def build_fallback_incident_from_findings(
    findings: list[dict[str, Any]],
    scan_paths: list[str],
) -> dict[str, Any] | None:
    if not findings:
        return None

    highest_severity = "medium"

    for finding in findings:
        severity = str(
            finding.get("severity_hint")
            or finding.get("severity")
            or "medium"
        ).lower()

        if severity_to_level(severity) > severity_to_level(highest_severity):
            highest_severity = severity

    affected_repos = sorted({
        str(finding.get("repo_name"))
        for finding in findings
        if finding.get("repo_name")
    })

    affected_files = sorted({
        str(finding.get("file"))
        for finding in findings
        if finding.get("file")
    })

    affected_endpoints = sorted({
        str(finding.get("endpoint"))
        for finding in findings
        if finding.get("endpoint")
    })

    affected_database_tables = sorted({
        str(finding.get("database_table"))
        for finding in findings
        if finding.get("database_table")
    })

    finding_types = sorted({
        str(finding.get("finding_type") or finding.get("type") or "unknown")
        for finding in findings
    })

    return {
        "incident_id": f"INC-{uuid4().hex[:8]}",
        "title": f"Repository scan detected {len(findings)} security finding(s)",
        "severity": highest_severity,
        "severity_level": severity_to_level(highest_severity),
        "confidence_score": 0.75,
        "confidence_reasons": [
            "Repository scanner detected one or more security findings.",
            f"Finding types: {', '.join(finding_types)}",
            f"Scanned paths: {', '.join(scan_paths)}",
        ],
        "confidence_limitations": [
            "This incident was created from scan findings because the correlator did not produce a grouped incident.",
        ],
        "affected_repos": affected_repos,
        "affected_files": affected_files,
        "affected_endpoints": affected_endpoints,
        "affected_database_tables": affected_database_tables,
        "findings": findings,
        "attack_path": {
            "nodes": [
                {
                    "id": "repo",
                    "label": "Scanned Repository",
                    "type": "infrastructure",
                },
                {
                    "id": "finding",
                    "label": "Security Finding",
                    "type": "runtime",
                },
                {
                    "id": "impact",
                    "label": "Potential Security Impact",
                    "type": "impact",
                },
            ],
            "edges": [
                {
                    "from": "repo",
                    "to": "finding",
                    "label": "contains",
                },
                {
                    "from": "finding",
                    "to": "impact",
                    "label": "may cause",
                },
            ],
        },
        "related_memory": [],
        "timestamp": utc_now(),
    }


def normalize_incident_for_frontend(incident: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(incident)

    findings = normalized.get("findings", [])

    if not isinstance(findings, list):
        findings = []

    findings = [
        normalize_scanner_finding(finding)
        for finding in findings
        if isinstance(finding, dict)
    ]

    severity = normalized.get("severity", "medium")

    if isinstance(severity, dict):
        severity_level = severity.get("level", 3)
        severity = (
            severity.get("level_name")
            or severity.get("name")
            or severity.get("label")
            or "medium"
        )
    else:
        severity_level = normalized.get(
            "severity_level",
            severity_to_level(str(severity)),
        )

    severity = str(severity).lower()

    affected_repos = sorted({
        str(finding.get("repo_name"))
        for finding in findings
        if finding.get("repo_name")
    })

    affected_files = sorted({
        str(finding.get("file"))
        for finding in findings
        if finding.get("file")
    })

    affected_endpoints = sorted({
        str(finding.get("endpoint"))
        for finding in findings
        if finding.get("endpoint")
    })

    affected_database_tables = sorted({
        str(finding.get("database_table"))
        for finding in findings
        if finding.get("database_table")
    })

    return {
        "incident_id": normalized.get("incident_id") or f"INC-{uuid4().hex[:8]}",
        "title": normalized.get("title") or "Repository security incident detected",
        "severity": severity,
        "severity_level": int(severity_level),
        "confidence_score": normalized.get("confidence_score", 0.5),
        "confidence_reasons": normalized.get(
            "confidence_reasons",
            ["Repository scan produced correlated security evidence."],
        ),
        "confidence_limitations": normalized.get("confidence_limitations", []),
        "affected_repos": normalized.get("affected_repos") or affected_repos,
        "affected_files": normalized.get("affected_files") or affected_files,
        "affected_endpoints": normalized.get("affected_endpoints") or affected_endpoints,
        "affected_database_tables": (
            normalized.get("affected_database_tables")
            or affected_database_tables
        ),
        "findings": findings,
        "attack_path": normalized.get("attack_path") or {"nodes": [], "edges": []},
        "related_memory": normalized.get("related_memory") or [],
        "timestamp": normalized.get("timestamp") or utc_now(),
    }

def build_fallback_incidents_from_findings(
    findings: list[dict[str, Any]],
    scan_paths: list[str],
) -> list[dict[str, Any]]:
    incidents: list[dict[str, Any]] = []

    for index, finding in enumerate(findings, start=1):
        severity = str(
            finding.get("severity_hint")
            or finding.get("severity")
            or "medium"
        ).lower()

        file_value = finding.get("file") or "unknown"
        finding_type = finding.get("finding_type") or finding.get("type") or "security_finding"

        incident = {
            "incident_id": f"INC-{uuid4().hex[:8]}",
            "title": f"Finding {index}: {finding_type} in {file_value}",
            "severity": severity,
            "severity_level": severity_to_level(severity),
            "confidence_score": 0.75,
            "confidence_reasons": [
                "Repository scanner detected this security finding.",
                f"Finding type: {finding_type}",
                f"Evidence: {finding.get('evidence', 'No evidence provided')}",
                f"Scanned paths: {', '.join(scan_paths)}",
            ],
            "confidence_limitations": [
                "This incident was generated directly from an individual scanner finding.",
            ],
            "affected_repos": [finding.get("repo_name")] if finding.get("repo_name") else [],
            "affected_files": [file_value] if file_value else [],
            "affected_endpoints": [finding.get("endpoint")] if finding.get("endpoint") else [],
            "affected_database_tables": (
                [finding.get("database_table")]
                if finding.get("database_table")
                else []
            ),
            "findings": [finding],
            "attack_path": {
                "nodes": [
                    {
                        "id": "repo",
                        "label": "Scanned Repository",
                        "type": "infrastructure",
                    },
                    {
                        "id": "finding",
                        "label": str(finding_type),
                        "type": "runtime",
                    },
                    {
                        "id": "impact",
                        "label": "Potential Security Impact",
                        "type": "impact",
                    },
                ],
                "edges": [
                    {
                        "from": "repo",
                        "to": "finding",
                        "label": "contains",
                    },
                    {
                        "from": "finding",
                        "to": "impact",
                        "label": "may cause",
                    },
                ],
            },
            "related_memory": [],
            "timestamp": utc_now(),
        }

        incidents.append(incident)

    return incidents

def run_repo_scan_pipeline(
    paths: list[str],
    use_mock: bool = False,
    use_bob: bool = True,
) -> dict[str, Any]:
    global bob_analysis_store

    resolved_paths = resolve_scan_paths(paths)

    findings_store.clear()
    incidents_store.clear()
    updates_store.clear()
    bob_analysis_store = None

    raw_findings = rust_scanner.scan(resolved_paths, use_mock=use_mock)

    if not isinstance(raw_findings, list):
        raw_findings = []

    findings = [
        normalize_scanner_finding(finding)
        for finding in raw_findings
        if isinstance(finding, dict)
    ]

    upsert_findings(findings)

    raw_incidents: list[dict[str, Any]] = []

    try:
        correlated = correlator.correlate(findings)

        if isinstance(correlated, list):
            raw_incidents = [
                incident
                for incident in correlated
                if isinstance(incident, dict)
            ]

    except Exception as error:
        print(f"[scan] Correlator failed, using fallback incident: {error}")
        raw_incidents = []

    incidents: list[dict[str, Any]] = []

    for raw_incident in raw_incidents:
        incident = normalize_incident_for_frontend(raw_incident)

        try:
            severity_info = classifier.classify(incident)
            incident["severity"] = str(
                severity_info.get("level_name", incident.get("severity", "medium"))
            ).lower()
            incident["severity_level"] = int(
                severity_info.get("level", incident.get("severity_level", 3))
            )
        except Exception:
            incident["severity"] = str(incident.get("severity", "medium")).lower()
            incident["severity_level"] = int(incident.get("severity_level", 3))

        try:
            confidence_info = confidence_scorer.calculate_confidence(incident)
            incident["confidence_score"] = confidence_info.get(
                "confidence_score",
                incident.get("confidence_score", 0.5),
            )
            incident["confidence_reasons"] = confidence_info.get(
                "confidence_reasons",
                incident.get("confidence_reasons", []),
            )
            incident["confidence_limitations"] = confidence_info.get(
                "confidence_limitations",
                incident.get("confidence_limitations", []),
            )
        except Exception:
            incident.setdefault("confidence_score", 0.5)
            incident.setdefault(
                "confidence_reasons",
                ["Scanner produced correlated evidence."],
            )
            incident.setdefault("confidence_limitations", [])

        try:
            incident["attack_path"] = attack_path_builder.build_attack_path(incident)
        except Exception:
            incident["attack_path"] = {"nodes": [], "edges": []}

        attach_related_memory(incident)
        upsert_incident(incident)
        incidents.append(incident)

    if not incidents and findings:
        fallback_incidents = build_fallback_incidents_from_findings(
            findings=findings,
            scan_paths=resolved_paths,
        )

        for fallback_incident in fallback_incidents:
            attach_related_memory(fallback_incident)
            upsert_incident(fallback_incident)
            incidents.append(fallback_incident)

    analysis = None
    analyses: list[dict[str, Any]] = []

    if use_bob and incidents:
        analyses = run_bob_reasoning_for_all_incidents(incidents)

        if analyses:
            analysis = analyses[0]["analysis"]
            bob_analysis_store = analysis

        global bob_analyses_store
        bob_analyses_store = analyses

    return {
        "run_id": f"SCAN-{uuid4().hex[:8]}",
        "resolved_paths": resolved_paths,
        "findings": findings,
        "incidents": incidents,
        "bob_analysis": analysis,
        "bob_analyses": analyses,
    }
def run_bob_reasoning_for_all_incidents(
    incidents: list[dict[str, Any]],
    max_reports: int = 10,
) -> list[dict[str, Any]]:
    """
    Runs Bob analysis for multiple incidents and returns a report list.

    max_reports prevents very large scans from making too many watsonx calls.
    """
    reports: list[dict[str, Any]] = []

    for incident in incidents[:max_reports]:
        analysis = run_bob_reasoning_for_incident(incident)

        reports.append(
            {
                "incident_id": incident.get("incident_id"),
                "incident_title": incident.get("title"),
                "finding_count": len(incident.get("findings", [])),
                "analysis": analysis,
            }
        )

    return reports
@app.post("/api/scan")
async def run_scan(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        paths = payload.get("paths", ["."])
        use_mock = bool(payload.get("use_mock", False))
        use_bob = bool(payload.get("use_bob", True))

        result = await asyncio.to_thread(
            run_repo_scan_pipeline,
            paths,
            use_mock,
            use_bob,
        )

        await ws_manager.broadcast(
            {
                "type": "scan_completed",
                "findings": findings_store,
                "incidents": incidents_store,
                "new_findings": result["findings"],
                "new_incidents": result["incidents"],
                "bob_analysis": result["bob_analysis"],
                "bob_analyses": result.get("bob_analyses", []),
            }
        )

        return {
            "status": "success",
            "message": "Repository scan completed",
            "run_id": result["run_id"],
            "paths": payload.get("paths", ["."]),
            "resolved_paths": result["resolved_paths"],
            "new_findings": result["findings"],
            "new_incidents": result["incidents"],
            "bob_analysis": result["bob_analysis"],
           "bob_analyses": result.get("bob_analyses", []),
            "total_findings": len(findings_store),
            "total_incidents": len(incidents_store),
            "memory_saved": (
                result["bob_analysis"].get("memory_saved", False)
                if isinstance(result["bob_analysis"], dict)
                else False
            ),
            "saved_memory_id": (
                result["bob_analysis"].get("saved_memory_id")
                if isinstance(result["bob_analysis"], dict)
                else None
            ),
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error),
            "paths": payload.get("paths", []),
            "new_findings": [],
            "new_incidents": [],
            "bob_analysis": None,
            "total_findings": len(findings_store),
            "total_incidents": len(incidents_store),
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
@app.get("/api/bob-analyses")
def get_all_bob_analyses() -> dict[str, Any]:
    return {
        "count": len(bob_analyses_store),
        "reports": bob_analyses_store,
    }