#!/usr/bin/env python3
"""
Test script for real-time monitoring
Simulates new findings and incidents to test WebSocket notifications
"""

import asyncio
import json
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api_server import manager, findings_db, incidents_db, notify_new_finding, notify_new_incident

async def simulate_attack_scenario():
    """Simulate a realistic attack scenario with multiple findings"""
    
    print("\n" + "="*60)
    print("🎭 SIMULATING ATTACK SCENARIO")
    print("="*60 + "\n")
    
    # Scenario 1: Hardcoded secret detected
    print("⏱️  T+0s: Detecting hardcoded secret...")
    finding1 = {
        "finding_id": "SIM-001",
        "repo_name": "test-backend",
        "finding_type": "hardcoded_secret",
        "category": "secret_exposure",
        "severity_hint": "high",
        "source": "rust_scanner",
        "file": "config/database.py",
        "line": 15,
        "endpoint": None,
        "database_table": None,
        "evidence": "Database password found in source code",
        "masked_value": "db_pass_****xyz",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    findings_db.append(finding1)
    await notify_new_finding(finding1)
    await asyncio.sleep(2)
    
    # Scenario 2: Suspicious API access
    print("⏱️  T+2s: Detecting suspicious API access...")
    finding2 = {
        "finding_id": "SIM-002",
        "repo_name": "test-backend",
        "finding_type": "runtime_anomaly",
        "category": "runtime_behavior",
        "severity_hint": "medium",
        "source": "log_analyzer",
        "file": None,
        "line": None,
        "endpoint": "/api/admin/users",
        "database_table": None,
        "evidence": "Unusual access pattern to admin endpoint",
        "masked_value": None,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    findings_db.append(finding2)
    await notify_new_finding(finding2)
    await asyncio.sleep(2)
    
    # Scenario 3: Database anomaly
    print("⏱️  T+4s: Detecting database anomaly...")
    finding3 = {
        "finding_id": "SIM-003",
        "repo_name": "test-backend",
        "finding_type": "database_anomaly",
        "category": "database_activity",
        "severity_hint": "high",
        "source": "db_monitor",
        "file": None,
        "line": None,
        "endpoint": None,
        "database_table": "users",
        "evidence": "Massive data export detected (10,000 rows)",
        "masked_value": None,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    findings_db.append(finding3)
    await notify_new_finding(finding3)
    await asyncio.sleep(2)
    
    # Scenario 4: Correlated incident
    print("⏱️  T+6s: Correlating findings into incident...")
    incident = {
        "incident_id": "SIM-INC-001",
        "title": "Potential data breach via compromised credentials",
        "severity": "critical",
        "severity_level": 5,
        "confidence_score": 0.92,
        "confidence_reasons": [
            "Hardcoded database password found in source code",
            "Suspicious admin endpoint access detected",
            "Large-scale data export from users table"
        ],
        "confidence_limitations": [
            "Unable to confirm if data was exfiltrated externally"
        ],
        "affected_repos": ["test-backend"],
        "affected_files": ["config/database.py"],
        "affected_endpoints": ["/api/admin/users"],
        "affected_database_tables": ["users"],
        "findings": [finding1, finding2, finding3],
        "attack_path": {
            "nodes": [
                {"id": "secret", "label": "Hardcoded Password", "type": "secret"},
                {"id": "access", "label": "Admin Access", "type": "api"},
                {"id": "export", "label": "Data Export", "type": "database"},
                {"id": "breach", "label": "Data Breach", "type": "impact"}
            ],
            "edges": [
                {"from": "secret", "to": "access", "label": "enables"},
                {"from": "access", "to": "export", "label": "triggers"},
                {"from": "export", "to": "breach", "label": "results in"}
            ]
        },
        "related_memory": [],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    incidents_db.append(incident)
    await notify_new_incident(incident)
    
    print("\n✅ Attack scenario simulation complete!")
    print(f"📊 Total findings: {len(findings_db)}")
    print(f"🚨 Total incidents: {len(incidents_db)}")
    print(f"👥 Connected clients: {len(manager.active_connections)}")
    print("\n" + "="*60 + "\n")

async def main():
    """Main test function"""
    print("\n🧪 Real-Time Monitoring Test Script")
    print("="*60)
    print("This script simulates security events to test WebSocket notifications")
    print("Make sure the API server is running and frontend is connected!")
    print("="*60 + "\n")
    
    # Wait for connections
    print("⏳ Waiting for WebSocket connections...")
    print("   Open the dashboard at http://localhost:5173")
    print("   Press Ctrl+C to start simulation\n")
    
    try:
        while len(manager.active_connections) == 0:
            await asyncio.sleep(1)
        
        print(f"✅ {len(manager.active_connections)} client(s) connected!\n")
        
        # Run simulation
        await simulate_attack_scenario()
        
    except KeyboardInterrupt:
        print("\n\n🎬 Starting simulation...\n")
        await simulate_attack_scenario()
    
    print("Test complete! Check the dashboard for notifications.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")

# Made with Bob
