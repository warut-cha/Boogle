from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional
from runtime_lab.mock_database import DB_PATH, init_db, reset_events
from src.realtime_detector import RealtimeAttackDetector
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4
from contextlib import asynccontextmanager
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
CONTRACTS_DIR = ROOT_DIR / "contracts"

findings_store: list[dict[str, Any]] = []
incidents_store: list[dict[str, Any]] = []
bob_analysis_store: dict[str, Any] | None = None
updates_store: list[dict[str, Any]] = []

# Request/Response Models
class ScanRequest(BaseModel):
    """Request model for triggering a security scan"""
    paths: list[str] = Field(..., min_items=1, description="Paths to scan")
    use_mock: bool = Field(default=True, description="Use mock data for testing")
    use_bob: bool = Field(default=True, description="Enable Bob AI analysis")

    @validator('paths')
    def validate_paths(cls, v):
        if not v:
            raise ValueError("At least one path must be provided")
        return v


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: dict[str, Any] = Field(..., description="Error details")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    uptime_seconds: Optional[float] = None
    findings_count: int = 0
    incidents_count: int = 0
    realtime_detector: dict[str, Any] = {}


# Metrics tracking
class APIMetrics:
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.scan_count = 0
        
    def record_request(self):
        self.request_count += 1
        
    def record_error(self):
        self.error_count += 1
        
    def record_scan(self):
        self.scan_count += 1
        
    def get_uptime(self) -> float:
        return time.time() - self.start_time
        
    def get_stats(self) -> dict[str, Any]:
        return {
            "uptime_seconds": self.get_uptime(),
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "total_scans": self.scan_count,
        }


metrics = APIMetrics()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Jeff API server...")
    init_db(reset=False)
    await realtime_detector.start()
    logger.info("Real-time attack detector started automatically.")

    try:
        yield
    finally:
        await realtime_detector.stop()
        logger.info("Real-time attack detector stopped.")
        logger.info("Jeff API server shutdown complete.")


app = FastAPI(
    title="Jeff API - AI-Powered Security Analyst",
    description="Backend API for Jeff security analysis system",
    version="1.0.0",
    lifespan=lifespan,
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all HTTP requests and track metrics"""
    start_time = time.time()
    metrics.record_request()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        metrics.record_error()
        logger.error(f"Request failed: {request.method} {request.url.path} - Error: {str(e)}")
        raise


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all unhandled exceptions"""
    metrics.record_error()
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if app.debug else "Please contact support",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        }
    )

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

realtime_detector = RealtimeAttackDetector(
    db_path=DB_PATH,
    findings_store=findings_store,
    incidents_store=incidents_store,
    ws_manager=ws_manager,
    poll_interval_seconds=1.0,
)
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

@app.post("/api/mock-db/init")
def init_mock_database(reset: bool = False) -> dict[str, str]:
    init_db(reset=reset)

    return {
        "status": "success",
        "message": "Mock database initialized",
    }

@app.get("/api/realtime/status")
def get_realtime_status() -> dict[str, Any]:
    return realtime_detector.status()


@app.post("/api/realtime/start")
async def start_realtime_detection() -> dict[str, Any]:
    init_db(reset=False)
    await realtime_detector.start()

    return {
        "status": "success",
        "message": "Real-time attack detection started",
        "detector": realtime_detector.status(),
    }


@app.post("/api/realtime/stop")
async def stop_realtime_detection() -> dict[str, Any]:
    await realtime_detector.stop()

    return {
        "status": "success",
        "message": "Real-time attack detection stopped",
        "detector": realtime_detector.status(),
    }


@app.delete("/api/mock-db/events")
async def clear_mock_database_events() -> dict[str, str]:
    reset_events()

    return {
        "status": "success",
        "message": "Mock database events cleared",
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for real-time updates
    
    Supports:
    - Real-time finding/incident notifications
    - Scan completion events
    - Bob analysis updates
    - Heartbeat/ping-pong for connection health
    """
    connected = await ws_manager.connect(websocket)

    if not connected:
        logger.warning("WebSocket connection rejected (invalid origin)")
        return

    client_id = id(websocket)
    logger.info(f"WebSocket client connected: {client_id}")

    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to Jeff API",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        
        while True:
            message = await websocket.receive_text()

            try:
                data = json.loads(message)
                msg_type = data.get("type")
                
                if msg_type == "ping":
                    # Respond to heartbeat
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })
                elif msg_type == "subscribe":
                    # Handle subscription requests (future feature)
                    logger.debug(f"Client {client_id} subscription: {data.get('channel')}")
                else:
                    logger.debug(f"Unknown message type from client {client_id}: {msg_type}")
                    
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from client {client_id}")
            except Exception as e:
                logger.error(f"Error processing message from client {client_id}: {str(e)}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {client_id}")
        ws_manager.disconnect(websocket)

    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {str(e)}", exc_info=True)
        ws_manager.disconnect(websocket)


@app.get("/api/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """
    Health check endpoint with system metrics
    Returns current system status and statistics
    """
    try:
        return HealthResponse(
            status="healthy",
            service="Jeff API",
            uptime_seconds=metrics.get_uptime(),
            findings_count=len(findings_store),
            incidents_count=len(incidents_store),
            realtime_detector=realtime_detector.status(),
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )


@app.get("/api/metrics")
def get_metrics() -> dict[str, Any]:
    """
    Get API metrics and statistics
    """
    return {
        **metrics.get_stats(),
        "findings_count": len(findings_store),
        "incidents_count": len(incidents_store),
        "active_websocket_connections": len(ws_manager.active_connections),
        "realtime_detector": realtime_detector.status(),
    }


@app.get("/api/findings")
def get_findings() -> list[dict[str, Any]]:
    """
    Get all security findings
    
    Returns:
        List of all findings in the system
    """
    logger.debug(f"Retrieving {len(findings_store)} findings")
    return findings_store


@app.get("/api/findings/{finding_id}")
def get_finding(finding_id: str) -> dict[str, Any]:
    """
    Get a specific finding by ID
    
    Args:
        finding_id: The unique identifier of the finding
        
    Returns:
        The finding details
        
    Raises:
        HTTPException: If finding not found
    """
    for finding in findings_store:
        if finding.get("finding_id") == finding_id:
            return finding
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Finding {finding_id} not found"
    )


@app.get("/api/incidents")
def get_incidents() -> list[dict[str, Any]]:
    """
    Get all security incidents
    
    Returns:
        List of all incidents in the system
    """
    logger.debug(f"Retrieving {len(incidents_store)} incidents")
    return incidents_store


@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id: str) -> dict[str, Any]:
    """
    Get a specific incident by ID
    
    Args:
        incident_id: The unique identifier of the incident
        
    Returns:
        The incident details with all related findings
        
    Raises:
        HTTPException: If incident not found
    """
    for incident in incidents_store:
        if incident.get("incident_id") == incident_id:
            logger.debug(f"Retrieved incident: {incident_id}")
            return incident

    logger.warning(f"Incident not found: {incident_id}")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Incident {incident_id} not found"
    )


@app.get("/api/incidents/{incident_id}/bob-analysis")
def get_bob_analysis(incident_id: str) -> dict[str, Any]:
    """
    Get Bob AI analysis for a specific incident
    
    Args:
        incident_id: The unique identifier of the incident
        
    Returns:
        Bob AI analysis including fixes, tests, and PR draft
    """
    # Verify incident exists
    incident_exists = any(
        inc.get("incident_id") == incident_id
        for inc in incidents_store
    )
    
    if not incident_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found"
        )
    
    analysis = bob_analysis_store or load_sample_bob_output()
    logger.debug(f"Retrieved Bob analysis for incident: {incident_id}")
    return analysis


@app.post("/api/incidents/{incident_id}/analyze-with-bob")
async def analyze_with_bob(incident_id: str) -> dict[str, Any]:
    """
    Trigger Bob AI analysis for a specific incident
    
    Args:
        incident_id: The unique identifier of the incident
        
    Returns:
        Bob AI analysis results
        
    Raises:
        HTTPException: If incident not found or analysis fails
    """
    global bob_analysis_store
    
    # Verify incident exists
    incident = None
    for inc in incidents_store:
        if inc.get("incident_id") == incident_id:
            incident = inc
            break
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found"
        )
    
    try:
        logger.info(f"Starting Bob analysis for incident: {incident_id}")
        bob_analysis_store = load_sample_bob_output()

        await ws_manager.broadcast(
            {
                "type": "bob_analysis",
                "incident_id": incident_id,
                "analysis": bob_analysis_store,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        
        logger.info(f"Bob analysis completed for incident: {incident_id}")
        return bob_analysis_store
        
    except Exception as e:
        logger.error(f"Bob analysis failed for {incident_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bob analysis failed: {str(e)}"
        )


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
async def run_scan(request: ScanRequest) -> dict[str, Any]:
    """
    Trigger a new security scan
    
    Args:
        request: Scan configuration including paths and options
        
    Returns:
        Scan results with findings, incidents, and Bob analysis
    """
    global bob_analysis_store
    
    try:
        logger.info(f"Starting scan for paths: {request.paths}")
        metrics.record_scan()
        
        run_id, new_findings, new_incidents, new_bob_output = prepare_scan_result()

        findings_store.extend(new_findings)
        incidents_store.extend(new_incidents)
        
        if request.use_bob:
            bob_analysis_store = new_bob_output
        else:
            bob_analysis_store = None

        message = {
            "type": "scan_completed",
            "run_id": run_id,
            "findings": new_findings,
            "incidents": new_incidents,
            "bob_analysis": bob_analysis_store,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        await ws_manager.broadcast(message)
        
        logger.info(
            f"Scan completed: {run_id} - "
            f"Findings: {len(new_findings)}, "
            f"Incidents: {len(new_incidents)}"
        )

        return {
            "status": "success",
            "message": "Security scan completed successfully",
            "run_id": run_id,
            "paths": request.paths,
            "new_findings": new_findings,
            "new_incidents": new_incidents,
            "bob_analysis": bob_analysis_store,
            "total_findings": len(findings_store),
            "total_incidents": len(incidents_store),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.error(f"Scan failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scan failed: {str(e)}"
        )


@app.delete("/api/reset")
async def reset_dashboard_data() -> dict[str, str]:
    global bob_analysis_store

    findings_store.clear()
    incidents_store.clear()
    updates_store.clear()
    bob_analysis_store = None

    reset_events()

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
        "message": "All stored dashboard data and mock DB events cleared",
    }