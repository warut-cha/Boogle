"""
Integration tests for API server and frontend connectivity
Tests the complete data flow from backend to frontend
"""

import pytest
import asyncio
import json
from pathlib import Path
from fastapi.testclient import TestClient
from websockets import connect as ws_connect
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from api_server import app, findings_store, incidents_store, bob_analysis_store


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_stores():
    """Clear data stores before each test"""
    findings_store.clear()
    incidents_store.clear()
    yield
    findings_store.clear()
    incidents_store.clear()


class TestHealthEndpoints:
    """Test health check and metrics endpoints"""

    def test_health_check(self, client):
        """Test basic health check"""
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Jeff API"
        assert "uptime_seconds" in data
        assert "findings_count" in data
        assert "incidents_count" in data

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint"""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "uptime_seconds" in data
        assert "total_requests" in data
        assert "findings_count" in data
        assert "incidents_count" in data


class TestFindingsEndpoints:
    """Test findings CRUD operations"""

    def test_get_findings_empty(self, client):
        """Test getting findings when store is empty"""
        response = client.get("/api/findings")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_findings_with_data(self, client):
        """Test getting findings with data"""
        # Add test finding
        test_finding = {
            "finding_id": "TEST-001",
            "repo_name": "test-repo",
            "finding_type": "hardcoded_secret",
            "category": "secret_exposure",
            "severity_hint": "high",
            "source": "rust_scanner",
            "file": "test.py",
            "line": 10,
            "endpoint": None,
            "database_table": None,
            "evidence": "Test evidence",
            "masked_value": "test_****",
            "timestamp": "2026-05-17T09:00:00Z"
        }
        findings_store.append(test_finding)

        response = client.get("/api/findings")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["finding_id"] == "TEST-001"

    def test_get_finding_by_id(self, client):
        """Test getting specific finding by ID"""
        test_finding = {
            "finding_id": "TEST-001",
            "repo_name": "test-repo",
            "finding_type": "hardcoded_secret",
            "category": "secret_exposure",
            "severity_hint": "high",
            "source": "rust_scanner",
            "file": "test.py",
            "line": 10,
            "endpoint": None,
            "database_table": None,
            "evidence": "Test evidence",
            "masked_value": "test_****",
            "timestamp": "2026-05-17T09:00:00Z"
        }
        findings_store.append(test_finding)

        response = client.get("/api/findings/TEST-001")
        assert response.status_code == 200
        assert response.json()["finding_id"] == "TEST-001"

    def test_get_finding_not_found(self, client):
        """Test getting non-existent finding"""
        response = client.get("/api/findings/NONEXISTENT")
        assert response.status_code == 404


class TestIncidentsEndpoints:
    """Test incidents CRUD operations"""

    def test_get_incidents_empty(self, client):
        """Test getting incidents when store is empty"""
        response = client.get("/api/incidents")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_incidents_with_data(self, client):
        """Test getting incidents with data"""
        test_incident = {
            "incident_id": "INC-001",
            "title": "Test Incident",
            "severity": "high",
            "severity_level": 4,
            "confidence_score": 0.85,
            "confidence_reasons": ["Test reason"],
            "confidence_limitations": [],
            "affected_repos": ["test-repo"],
            "affected_files": ["test.py"],
            "affected_endpoints": [],
            "affected_database_tables": [],
            "findings": [],
            "attack_path": {"nodes": [], "edges": []},
            "related_memory": [],
            "timestamp": "2026-05-17T09:00:00Z"
        }
        incidents_store.append(test_incident)

        response = client.get("/api/incidents")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["incident_id"] == "INC-001"

    def test_get_incident_by_id(self, client):
        """Test getting specific incident by ID"""
        test_incident = {
            "incident_id": "INC-001",
            "title": "Test Incident",
            "severity": "high",
            "severity_level": 4,
            "confidence_score": 0.85,
            "confidence_reasons": ["Test reason"],
            "confidence_limitations": [],
            "affected_repos": ["test-repo"],
            "affected_files": ["test.py"],
            "affected_endpoints": [],
            "affected_database_tables": [],
            "findings": [],
            "attack_path": {"nodes": [], "edges": []},
            "related_memory": [],
            "timestamp": "2026-05-17T09:00:00Z"
        }
        incidents_store.append(test_incident)

        response = client.get("/api/incidents/INC-001")
        assert response.status_code == 200
        assert response.json()["incident_id"] == "INC-001"

    def test_get_incident_not_found(self, client):
        """Test getting non-existent incident"""
        response = client.get("/api/incidents/NONEXISTENT")
        assert response.status_code == 404


class TestScanEndpoint:
    """Test scan triggering"""

    def test_trigger_scan(self, client):
        """Test triggering a security scan"""
        response = client.post(
            "/api/scan",
            json={
                "paths": ["./mock-repos"],
                "use_mock": True,
                "use_bob": True
            }
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "run_id" in data
        assert "new_findings" in data
        assert "new_incidents" in data
        assert "bob_analysis" in data
        assert len(data["new_findings"]) > 0
        assert len(data["new_incidents"]) > 0

    def test_trigger_scan_without_bob(self, client):
        """Test scan without Bob analysis"""
        response = client.post(
            "/api/scan",
            json={
                "paths": ["./mock-repos"],
                "use_mock": True,
                "use_bob": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["bob_analysis"] is None

    def test_trigger_scan_invalid_request(self, client):
        """Test scan with invalid request"""
        response = client.post(
            "/api/scan",
            json={
                "paths": [],  # Empty paths should fail validation
                "use_mock": True,
                "use_bob": True
            }
        )
        
        assert response.status_code == 422  # Validation error


class TestBobAnalysisEndpoints:
    """Test Bob AI analysis endpoints"""

    def test_get_bob_analysis(self, client):
        """Test getting Bob analysis"""
        # Add test incident
        test_incident = {
            "incident_id": "INC-001",
            "title": "Test Incident",
            "severity": "high",
            "severity_level": 4,
            "confidence_score": 0.85,
            "confidence_reasons": [],
            "confidence_limitations": [],
            "affected_repos": [],
            "affected_files": [],
            "affected_endpoints": [],
            "affected_database_tables": [],
            "findings": [],
            "attack_path": {"nodes": [], "edges": []},
            "related_memory": []
        }
        incidents_store.append(test_incident)

        response = client.get("/api/incidents/INC-001/bob-analysis")
        assert response.status_code == 200
        
        data = response.json()
        assert "attack_type" in data
        assert "recommended_fixes" in data

    def test_get_bob_analysis_incident_not_found(self, client):
        """Test Bob analysis for non-existent incident"""
        response = client.get("/api/incidents/NONEXISTENT/bob-analysis")
        assert response.status_code == 404

    def test_trigger_bob_analysis(self, client):
        """Test triggering Bob analysis"""
        # Add test incident
        test_incident = {
            "incident_id": "INC-001",
            "title": "Test Incident",
            "severity": "high",
            "severity_level": 4,
            "confidence_score": 0.85,
            "confidence_reasons": [],
            "confidence_limitations": [],
            "affected_repos": [],
            "affected_files": [],
            "affected_endpoints": [],
            "affected_database_tables": [],
            "findings": [],
            "attack_path": {"nodes": [], "edges": []},
            "related_memory": []
        }
        incidents_store.append(test_incident)

        response = client.post("/api/incidents/INC-001/analyze-with-bob")
        assert response.status_code == 200
        
        data = response.json()
        assert "attack_type" in data
        assert "recommended_fixes" in data


class TestResetEndpoint:
    """Test data reset functionality"""

    def test_reset_data(self, client):
        """Test resetting all data"""
        # Add some test data
        findings_store.append({"finding_id": "TEST-001"})
        incidents_store.append({"incident_id": "INC-001"})

        response = client.delete("/api/reset")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        
        # Verify stores are cleared
        assert len(findings_store) == 0
        assert len(incidents_store) == 0


class TestRealtimeEndpoints:
    """Test real-time detection endpoints"""

    def test_realtime_status(self, client):
        """Test getting real-time detector status"""
        response = client.get("/api/realtime/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "running" in data
        assert "last_event_id" in data


class TestCORSHeaders:
    """Test CORS configuration"""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present"""
        response = client.options(
            "/api/health",
            headers={"Origin": "http://localhost:5173"}
        )
        
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers


class TestErrorHandling:
    """Test error handling"""

    def test_404_error(self, client):
        """Test 404 error handling"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Test method not allowed"""
        response = client.put("/api/health")
        assert response.status_code == 405


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
