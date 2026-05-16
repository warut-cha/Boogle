#!/usr/bin/env python3
"""
Flask API Server with Server-Sent Events (SSE) for Real-Time Dashboard Updates
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import json
import time
import threading
from queue import Queue
from datetime import datetime
from typing import List, Dict, Any
import yaml

# Import core modules
from scanners.rust_scanner_client import RustScannerClient
from correlators.incident_correlator import IncidentCorrelator
from correlators.attack_path_builder import AttackPathBuilder
from classifiers.severity_classifier import SeverityClassifier
from classifiers.confidence_scorer import ConfidenceScorer
from ai_engine.reasoning_engine import ReasoningEngine
from reporters.incident_reporter import IncidentReporter
from ai_engine.memory_manager import MemoryManager

# Load configuration
def load_config():
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

CONFIG = load_config()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Global state for real-time updates
class EventBroadcaster:
    def __init__(self):
        self.listeners = []
        self.findings = []
        self.incidents = []
        self.lock = threading.Lock()
    
    def add_listener(self, queue: Queue):
        with self.lock:
            self.listeners.append(queue)
    
    def remove_listener(self, queue: Queue):
        with self.lock:
            if queue in self.listeners:
                self.listeners.remove(queue)
    
    def broadcast(self, event_type: str, data: Any):
        """Broadcast event to all connected clients"""
        with self.lock:
            event = {
                'type': event_type,
                'data': data,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            # Remove disconnected listeners
            self.listeners = [q for q in self.listeners if not q.full()]
            for queue in self.listeners:
                try:
                    queue.put(event)
                except:
                    pass
    
    def add_finding(self, finding: Dict):
        with self.lock:
            self.findings.append(finding)
        self.broadcast('finding_added', finding)
    
    def add_incident(self, incident: Dict):
        with self.lock:
            self.incidents.append(incident)
        self.broadcast('incident_added', incident)
    
    def update_incident(self, incident: Dict):
        with self.lock:
            for i, inc in enumerate(self.incidents):
                if inc['incident_id'] == incident['incident_id']:
                    self.incidents[i] = incident
                    break
        self.broadcast('incident_updated', incident)
    
    def get_findings(self) -> List[Dict]:
        with self.lock:
            return self.findings.copy()
    
    def get_incidents(self) -> List[Dict]:
        with self.lock:
            return self.incidents.copy()
    
    def clear_all(self):
        with self.lock:
            self.findings = []
            self.incidents = []
        self.broadcast('data_cleared', {})

broadcaster = EventBroadcaster()

# SSE endpoint for real-time updates
@app.route('/api/events')
def sse_events():
    """Server-Sent Events endpoint for real-time updates"""
    def event_stream():
        queue = Queue(maxsize=50)
        broadcaster.add_listener(queue)
        
        try:
            # Send initial connection message
            yield f"data: {json.dumps({'type': 'connected', 'message': 'Real-time updates enabled'})}\n\n"
            
            # Stream events
            while True:
                try:
                    event = queue.get(timeout=30)
                    yield f"data: {json.dumps(event)}\n\n"
                except:
                    # Send heartbeat to keep connection alive
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.utcnow().isoformat() + 'Z'})}\n\n"
        finally:
            broadcaster.remove_listener(queue)
    
    return Response(event_stream(), mimetype='text/event-stream')

# REST API endpoints
@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'findings_count': len(broadcaster.get_findings()),
        'incidents_count': len(broadcaster.get_incidents())
    })

@app.route('/api/findings')
def get_findings():
    """Get all security findings"""
    return jsonify(broadcaster.get_findings())

@app.route('/api/incidents')
def get_incidents():
    """Get all correlated incidents"""
    return jsonify(broadcaster.get_incidents())

@app.route('/api/incidents/<incident_id>')
def get_incident(incident_id):
    """Get specific incident details"""
    incidents = broadcaster.get_incidents()
    incident = next((i for i in incidents if i['incident_id'] == incident_id), None)
    
    if incident:
        return jsonify(incident)
    return jsonify({'error': 'Incident not found'}), 404

@app.route('/api/incidents/<incident_id>/analyze-with-bob', methods=['POST'])
def analyze_with_bob(incident_id):
    """Trigger Bob AI analysis for an incident"""
    incidents = broadcaster.get_incidents()
    incident = next((i for i in incidents if i['incident_id'] == incident_id), None)
    
    if not incident:
        return jsonify({'error': 'Incident not found'}), 404
    
    try:
        # Run Bob AI reasoning
        reasoning_engine = ReasoningEngine(CONFIG['ai_engine'])
        enhanced_incidents = reasoning_engine.enhance_analysis([incident])
        
        if enhanced_incidents:
            enhanced_incident = enhanced_incidents[0]
            broadcaster.update_incident(enhanced_incident)
            return jsonify(enhanced_incident.get('bob_analysis', {}))
        
        return jsonify({'error': 'Analysis failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan', methods=['POST'])
def trigger_scan():
    """Trigger a new security scan"""
    data = request.get_json()
    paths = data.get('paths', ['./mock-repos'])
    use_mock = data.get('use_mock', False)
    use_bob = data.get('use_bob', True)
    
    # Run scan in background thread
    def run_scan():
        try:
            # Clear previous data
            broadcaster.clear_all()
            
            # Step 1: Run scanner
            rust_scanner = RustScannerClient()
            findings = rust_scanner.scan(paths, use_mock=use_mock)
            
            # Add findings one by one with delay for demo effect
            for finding in findings:
                broadcaster.add_finding(finding)
                time.sleep(0.5)  # Delay for visual effect
            
            # Step 2: Correlate incidents
            correlator = IncidentCorrelator(CONFIG['analysis']['correlation'])
            incidents = correlator.correlate(findings)
            
            # Step 3: Classify severity
            classifier = SeverityClassifier(CONFIG['severity'])
            for incident in incidents:
                severity_info = classifier.classify(incident)
                incident['severity'] = severity_info['level_name']
                incident['severity_level'] = severity_info['level']
            
            # Step 4: Calculate confidence
            confidence_scorer = ConfidenceScorer()
            for incident in incidents:
                confidence_info = confidence_scorer.calculate_confidence(incident)
                incident['confidence_score'] = confidence_info['confidence_score']
                incident['confidence_reasons'] = confidence_info['confidence_reasons']
                incident['confidence_limitations'] = confidence_info['confidence_limitations']
            
            # Step 5: Build attack paths
            attack_path_builder = AttackPathBuilder()
            for incident in incidents:
                attack_path = attack_path_builder.build_attack_path(incident)
                incident['attack_path'] = attack_path
            
            # Add incidents with delay
            for incident in incidents:
                broadcaster.add_incident(incident)
                time.sleep(1)  # Delay for visual effect
            
            # Step 6: AI reasoning (if enabled)
            if use_bob and incidents:
                reasoning_engine = ReasoningEngine(CONFIG['ai_engine'])
                enhanced_incidents = reasoning_engine.enhance_analysis(incidents)
                
                for enhanced_incident in enhanced_incidents:
                    broadcaster.update_incident(enhanced_incident)
                    time.sleep(0.5)
            
            broadcaster.broadcast('scan_complete', {
                'findings_count': len(findings),
                'incidents_count': len(incidents)
            })
            
        except Exception as e:
            broadcaster.broadcast('scan_error', {'error': str(e)})
    
    thread = threading.Thread(target=run_scan, daemon=True)
    thread.start()
    
    return jsonify({
        'status': 'scan_started',
        'message': 'Security scan initiated. Connect to /api/events for real-time updates.'
    })

@app.route('/api/demo/simulate-attack', methods=['POST'])
def simulate_attack():
    """Simulate a real-time attack scenario for demo purposes - Extended 60 second demo"""
    def simulate():
        broadcaster.clear_all()
        
        # Extended demo with 60 seconds of realistic security events
        timestamp_base = time.time()
        
        # Phase 1: Initial reconnaissance (0-10 seconds)
        demo_events = [
            # T+0s: Port scanning detected
            {
                "type": "finding",
                "delay": 0,
                "data": {
                    "finding_id": f"FIND-{int(timestamp_base)}-001",
                    "repo_name": "infra-config",
                    "finding_type": "infrastructure_risk",
                    "category": "infrastructure",
                    "severity_hint": "low",
                    "source": "rust_scanner",
                    "file": "docker-compose.yml",
                    "line": 23,
                    "endpoint": None,
                    "database_table": None,
                    "evidence": "Exposed port 5432 (PostgreSQL) without firewall rules",
                    "masked_value": None,
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
            },
            # T+2s: Suspicious log pattern
            {
                "type": "finding",
                "delay": 2,
                "data": {
                    "finding_id": f"FIND-{int(timestamp_base)}-002",
                    "repo_name": "legacy-backend",
                    "finding_type": "runtime_anomaly",
                    "category": "runtime_behavior",
                    "severity_hint": "medium",
                    "source": "python_analyzer",
                    "file": None,
                    "line": None,
                    "endpoint": "/api/v1/health",
                    "database_table": None,
                    "evidence": "Unusual traffic pattern: 150 requests from single IP in 30 seconds",
                    "masked_value": None,
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
            },
            # T+4s: Hardcoded AWS credentials
            {
                "type": "finding",
                "delay": 2,
                "data": {
                    "finding_id": f"FIND-{int(timestamp_base)}-003",
                    "repo_name": "frontend-app",
                    "finding_type": "hardcoded_secret",
                    "category": "secret_exposure",
                    "severity_hint": "critical",
                    "source": "rust_scanner",
                    "file": "src/api/client.ts",
                    "line": 8,
                    "endpoint": None,
                    "database_table": None,
                    "evidence": "AWS Access Key ID exposed in frontend code",
                    "masked_value": "AKIA****EXAMPLE",
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
            },
            # T+6s: SQL injection attempt
            {
                "type": "finding",
                "delay": 2,
                "data": {
                    "finding_id": f"FIND-{int(timestamp_base)}-004",
                    "repo_name": "legacy-backend",
                    "finding_type": "runtime_anomaly",
                    "category": "runtime_behavior",
                    "severity_hint": "high",
                    "source": "python_analyzer",
                    "file": None,
                    "line": None,
                    "endpoint": "/api/v1/search",
                    "database_table": "users",
                    "evidence": "SQL injection pattern detected in query parameter: ' OR '1'='1",
                    "masked_value": None,
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
            },
            # T+8s: First incident - Infrastructure exposure
            {
                "type": "incident",
                "delay": 2,
                "data": {
                    "incident_id": f"INC-{int(timestamp_base)}-001",
                    "title": "Database port exposed without authentication",
                    "severity": "medium",
                    "severity_level": 3,
                    "confidence_score": 0.75,
                    "confidence_reasons": [
                        "PostgreSQL port 5432 publicly accessible",
                        "No firewall rules configured",
                        "Default credentials may be in use"
                    ],
                    "confidence_limitations": [
                        "Unable to verify if default credentials are active"
                    ],
                    "affected_repos": ["infra-config"],
                    "affected_files": ["docker-compose.yml"],
                    "affected_endpoints": [],
                    "affected_database_tables": [],
                    "findings": [],
                    "attack_path": {
                        "nodes": [
                            {"id": "port", "label": "Exposed Port 5432", "type": "infrastructure"},
                            {"id": "db", "label": "PostgreSQL Database", "type": "database"}
                        ],
                        "edges": [
                            {"from": "port", "to": "db", "label": "exposes"}
                        ]
                    },
                    "related_memory": [],
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
            },
            # T+12s: Deprecated API found
            {
                "type": "finding",
                "delay": 4,
                "data": {
                    "finding_id": f"FIND-{int(timestamp_base)}-005",
                    "repo_name": "legacy-backend",
                    "finding_type": "deprecated_api",
                    "category": "legacy_api",
                    "severity_hint": "medium",
                    "source": "python_analyzer",
                    "file": "legacy/old_export_api.py",
                    "line": 15,
                    "endpoint": "/api/v1/export-users",
                    "database_table": None,
                    "evidence": "Deprecated export endpoint still accessible, marked for removal 6 months ago",
                    "masked_value": None,
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
            },
            # T+15s: API key in logs
            {
                "type": "finding",
                "delay": 3,
                "data": {
                    "finding_id": f"FIND-{int(timestamp_base)}-006",
                    "repo_name": "legacy-backend",
                    "finding_type": "sensitive_log_exposure",
                    "category": "logging",
                    "severity_hint": "high",
                    "source": "python_analyzer",
                    "file": "logs/api_logs.json",
                    "line": 1247,
                    "endpoint": None,
                    "database_table": None,
                    "evidence": "API key logged in plaintext in application logs",
                    "masked_value": "sk_live_****8h3k",
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
            },
            # T+18s: Database anomaly
            {
                "type": "finding",
                "delay": 3,
                "data": {
                    "finding_id": f"FIND-{int(timestamp_base)}-007",
                    "repo_name": "legacy-backend",
                    "finding_type": "database_anomaly",
                    "category": "database_activity",
                    "severity_hint": "high",
                    "source": "python_analyzer",
                    "file": None,
                    "line": None,
                    "endpoint": None,
                    "database_table": "users",
                    "evidence": "Abnormal read spike: 50,000 rows accessed in 2 minutes",
                    "masked_value": None,
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
            },
            # T+22s: SSH private key exposed
            {
                "type": "finding",
                "delay": 4,
                "data": {
                    "finding_id": f"FIND-{int(timestamp_base)}-008",
                    "repo_name": "infra-config",
                    "finding_type": "private_key",
                    "category": "secret_exposure",
                    "severity_hint": "critical",
                    "source": "rust_scanner",
                    "file": ".github/deploy_key",
                    "line": 1,
                    "endpoint": None,
                    "database_table": None,
                    "evidence": "RSA private key committed to repository",
                    "masked_value": "-----BEGIN RSA PRIVATE KEY-----",
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
            },
            # T+25s: Second incident - Credential leakage
            {
                "type": "incident",
                "delay": 3,
                "data": {
                    "incident_id": f"INC-{int(timestamp_base)}-002",
                    "title": "Critical: Multiple credentials exposed in codebase",
                    "severity": "critical",
                    "severity_level": 5,
                    "confidence_score": 0.95,
                    "confidence_reasons": [
                        "AWS credentials found in frontend code",
                        "API key logged in plaintext",
                        "SSH private key in repository",
                        "All credentials are production keys"
                    ],
                    "confidence_limitations": [],
                    "affected_repos": ["frontend-app", "legacy-backend", "infra-config"],
                    "affected_files": ["src/api/client.ts", "logs/api_logs.json", ".github/deploy_key"],
                    "affected_endpoints": [],
                    "affected_database_tables": [],
                    "findings": [],
                    "attack_path": {
                        "nodes": [
                            {"id": "aws", "label": "AWS Credentials", "type": "secret"},
                            {"id": "api_key", "label": "API Key in Logs", "type": "secret"},
                            {"id": "ssh", "label": "SSH Private Key", "type": "secret"},
                            {"id": "breach", "label": "Potential Breach", "type": "impact"}
                        ],
                        "edges": [
                            {"from": "aws", "to": "breach", "label": "enables"},
                            {"from": "api_key", "to": "breach", "label": "enables"},
                            {"from": "ssh", "to": "breach", "label": "enables"}
                        ]
                    },
                    "related_memory": [],
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
            },
            # T+30s: Brute force attempt
            {
                "type": "finding",
                "delay": 5,
                "data": {
                    "finding_id": f"FIND-{int(timestamp_base)}-009",
                    "repo_name": "legacy-backend",
                    "finding_type": "runtime_anomaly",
                    "category": "runtime_behavior",
                    "severity_hint": "high",
                    "source": "python_analyzer",
                    "file": None,
                    "line": None,
                    "endpoint": "/api/v1/login",
                    "database_table": None,
                    "evidence": "Brute force attack detected: 500 failed login attempts from 192.168.1.100",
                    "masked_value": None,
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
            },
            # T+33s: Unauthorized API access
            {
                "type": "finding",
                "delay": 3,
                "data": {
                    "finding_id": f"FIND-{int(timestamp_base)}-010",
                    "repo_name": "legacy-backend",
                    "finding_type": "runtime_anomaly",
                    "category": "runtime_behavior",
                    "severity_hint": "critical",
                    "source": "python_analyzer",
                    "file": None,
                    "line": None,
                    "endpoint": "/api/v1/export-users",
                    "database_table": "users",
                    "evidence": "Unauthorized access to deprecated export endpoint using leaked credentials",
                    "masked_value": None,
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
            },
            # T+37s: Data exfiltration detected
            {
                "type": "finding",
                "delay": 4,
                "data": {
                    "finding_id": f"FIND-{int(timestamp_base)}-011",
                    "repo_name": "legacy-backend",
                    "finding_type": "database_anomaly",
                    "category": "database_activity",
                    "severity_hint": "critical",
                    "source": "python_analyzer",
                    "file": None,
                    "line": None,
                    "endpoint": None,
                    "database_table": "users",
                    "evidence": "Large data export detected: 100,000 user records downloaded",
                    "masked_value": None,
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
            },
            # T+42s: Third incident - Active data breach
            {
                "type": "incident",
                "delay": 5,
                "data": {
                    "incident_id": f"INC-{int(timestamp_base)}-003",
                    "title": "ACTIVE BREACH: Coordinated attack with data exfiltration",
                    "severity": "critical",
                    "severity_level": 5,
                    "confidence_score": 0.98,
                    "confidence_reasons": [
                        "Brute force attack succeeded using leaked credentials",
                        "Deprecated API exploited for unauthorized access",
                        "Large-scale data exfiltration confirmed",
                        "Attack chain fully correlated across multiple systems",
                        "Active exploitation in progress"
                    ],
                    "confidence_limitations": [],
                    "affected_repos": ["legacy-backend", "frontend-app"],
                    "affected_files": ["legacy/old_export_api.py", "src/api/client.ts"],
                    "affected_endpoints": ["/api/v1/export-users", "/api/v1/login"],
                    "affected_database_tables": ["users"],
                    "findings": [],
                    "attack_path": {
                        "nodes": [
                            {"id": "recon", "label": "Reconnaissance", "type": "runtime"},
                            {"id": "creds", "label": "Leaked Credentials", "type": "secret"},
                            {"id": "brute", "label": "Brute Force Attack", "type": "runtime"},
                            {"id": "api", "label": "Deprecated API", "type": "api"},
                            {"id": "db", "label": "Database Access", "type": "database"},
                            {"id": "exfil", "label": "Data Exfiltration", "type": "impact"}
                        ],
                        "edges": [
                            {"from": "recon", "to": "creds", "label": "discovers"},
                            {"from": "creds", "to": "brute", "label": "enables"},
                            {"from": "brute", "to": "api", "label": "exploits"},
                            {"from": "api", "to": "db", "label": "accesses"},
                            {"from": "db", "to": "exfil", "label": "leads to"}
                        ]
                    },
                    "related_memory": [],
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
            },
            # T+48s: Additional findings during investigation
            {
                "type": "finding",
                "delay": 6,
                "data": {
                    "finding_id": f"FIND-{int(timestamp_base)}-012",
                    "repo_name": "infra-config",
                    "finding_type": "infrastructure_risk",
                    "category": "infrastructure",
                    "severity_hint": "medium",
                    "source": "rust_scanner",
                    "file": "Dockerfile",
                    "line": 12,
                    "endpoint": None,
                    "database_table": None,
                    "evidence": "Container running as root user, privilege escalation risk",
                    "masked_value": None,
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
            },
            # T+52s: Weak encryption detected
            {
                "type": "finding",
                "delay": 4,
                "data": {
                    "finding_id": f"FIND-{int(timestamp_base)}-013",
                    "repo_name": "legacy-backend",
                    "finding_type": "hardcoded_secret",
                    "category": "secret_exposure",
                    "severity_hint": "high",
                    "source": "python_analyzer",
                    "file": "legacy/crypto_utils.py",
                    "line": 45,
                    "endpoint": None,
                    "database_table": None,
                    "evidence": "Weak encryption key hardcoded: MD5 hash used for password storage",
                    "masked_value": "md5_****_weak",
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
            },
            # T+56s: Debug mode in production
            {
                "type": "finding",
                "delay": 4,
                "data": {
                    "finding_id": f"FIND-{int(timestamp_base)}-014",
                    "repo_name": "frontend-app",
                    "finding_type": "infrastructure_risk",
                    "category": "infrastructure",
                    "severity_hint": "medium",
                    "source": "rust_scanner",
                    "file": "src/api/client.ts",
                    "line": 3,
                    "endpoint": None,
                    "database_table": None,
                    "evidence": "Debug mode enabled in production build, exposing stack traces",
                    "masked_value": None,
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
            },
            # T+60s: Final incident - Security posture assessment
            {
                "type": "incident",
                "delay": 4,
                "data": {
                    "incident_id": f"INC-{int(timestamp_base)}-004",
                    "title": "Critical security posture issues across infrastructure",
                    "severity": "high",
                    "severity_level": 4,
                    "confidence_score": 0.88,
                    "confidence_reasons": [
                        "Multiple infrastructure misconfigurations detected",
                        "Weak cryptography in use",
                        "Debug mode enabled in production",
                        "Container security issues present"
                    ],
                    "confidence_limitations": [
                        "Full infrastructure audit not yet complete"
                    ],
                    "affected_repos": ["infra-config", "legacy-backend", "frontend-app"],
                    "affected_files": ["Dockerfile", "legacy/crypto_utils.py", "src/api/client.ts"],
                    "affected_endpoints": [],
                    "affected_database_tables": [],
                    "findings": [],
                    "attack_path": {
                        "nodes": [
                            {"id": "root", "label": "Root Container", "type": "infrastructure"},
                            {"id": "weak", "label": "Weak Encryption", "type": "secret"},
                            {"id": "debug", "label": "Debug Mode", "type": "infrastructure"},
                            {"id": "risk", "label": "Elevated Risk", "type": "impact"}
                        ],
                        "edges": [
                            {"from": "root", "to": "risk", "label": "increases"},
                            {"from": "weak", "to": "risk", "label": "increases"},
                            {"from": "debug", "to": "risk", "label": "increases"}
                        ]
                    },
                    "related_memory": [],
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
            }
        ]
        
        # Process all events with their delays
        for event in demo_events:
            time.sleep(event["delay"])
            
            if event["type"] == "finding":
                broadcaster.add_finding(event["data"])
                broadcaster.broadcast('demo_progress', {
                    'message': f'🔍 {event["data"]["finding_type"]}: {event["data"]["evidence"][:50]}...',
                    'severity': event["data"]["severity_hint"]
                })
            elif event["type"] == "incident":
                broadcaster.add_incident(event["data"])
                broadcaster.broadcast('demo_progress', {
                    'message': f'🚨 Incident: {event["data"]["title"]}',
                    'severity': event["data"]["severity"]
                })
        
        broadcaster.broadcast('demo_complete', {
            'message': 'Extended security simulation complete',
            'duration': '60 seconds',
            'findings_count': 14,
            'incidents_count': 4
        })
    
    thread = threading.Thread(target=simulate, daemon=True)
    thread.start()
    
    return jsonify({
        'status': 'simulation_started',
        'message': 'Extended 60-second security simulation started. Watch the dashboard for real-time updates!',
        'duration': '60 seconds',
        'expected_findings': 14,
        'expected_incidents': 4
    })

@app.route('/api/demo/simulate-attack-old', methods=['POST'])
def simulate_attack_old():
    """Original short demo - kept for backwards compatibility"""
    def simulate():
        # Original 10-second demo
        demo_findings = [
            {
                "finding_id": f"FIND-{int(time.time())}-001",
                "repo_name": "legacy-backend",
                "finding_type": "hardcoded_secret",
                "category": "secret_exposure",
                "severity_hint": "high",
                "source": "rust_scanner",
                "file": "legacy/old_export_api.py",
                "line": 12,
                "endpoint": "/api/v1/export-users",
                "database_table": None,
                "evidence": "Hardcoded API key detected",
                "masked_value": "sk_test_****92fa",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            },
            {
                "finding_id": f"FIND-{int(time.time())}-002",
                "repo_name": "legacy-backend",
                "finding_type": "deprecated_api",
                "category": "legacy_api",
                "severity_hint": "medium",
                "source": "python_analyzer",
                "file": "legacy/old_export_api.py",
                "line": 8,
                "endpoint": "/api/v1/export-users",
                "database_table": None,
                "evidence": "Deprecated export endpoint still accessible",
                "masked_value": None,
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            },
            {
                "finding_id": f"FIND-{int(time.time())}-003",
                "repo_name": "legacy-backend",
                "finding_type": "runtime_anomaly",
                "category": "runtime_behavior",
                "severity_hint": "high",
                "source": "python_analyzer",
                "file": None,
                "line": None,
                "endpoint": "/api/v1/export-users",
                "database_table": None,
                "evidence": "Suspicious repeated access to deprecated endpoint",
                "masked_value": None,
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }
        ]
        
        broadcaster.clear_all()
        
        for i, finding in enumerate(demo_findings):
            time.sleep(2)  # 2 second delay between findings
            broadcaster.add_finding(finding)
            broadcaster.broadcast('demo_progress', {
                'step': i + 1,
                'total': len(demo_findings),
                'message': f'Detected: {finding["finding_type"]}'
            })
        
        # Create incident after all findings
        time.sleep(2)
        incident = {
            "incident_id": f"INC-{int(time.time())}",
            "title": "Real-time attack detected: Credential leakage through abandoned API",
            "severity": "critical",
            "severity_level": 5,
            "confidence_score": 0.92,
            "confidence_reasons": [
                "Multiple correlated security signals detected",
                "Active exploitation pattern identified",
                "Sensitive data exposure confirmed"
            ],
            "confidence_limitations": [],
            "affected_repos": ["legacy-backend"],
            "affected_files": ["legacy/old_export_api.py"],
            "affected_endpoints": ["/api/v1/export-users"],
            "affected_database_tables": [],
            "findings": demo_findings,
            "attack_path": {
                "nodes": [
                    {"id": "secret", "label": "Hardcoded Secret", "type": "secret"},
                    {"id": "api", "label": "Deprecated API", "type": "api"},
                    {"id": "exploit", "label": "Active Exploitation", "type": "runtime"}
                ],
                "edges": [
                    {"from": "secret", "to": "api", "label": "enables"},
                    {"from": "api", "to": "exploit", "label": "exploited by"}
                ]
            },
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
        
        broadcaster.add_incident(incident)
        broadcaster.broadcast('demo_complete', {
            'message': 'Attack simulation complete',
            'incident_id': incident['incident_id']
        })
    
    thread = threading.Thread(target=simulate, daemon=True)
    thread.start()
    
    return jsonify({
        'status': 'simulation_started',
        'message': 'Attack simulation started. Watch the dashboard for real-time updates!'
    })

@app.route('/api/clear', methods=['POST'])
def clear_data():
    """Clear all findings and incidents"""
    broadcaster.clear_all()
    return jsonify({'status': 'cleared', 'message': 'All data cleared'})

if __name__ == '__main__':
    print("🚀 Bob Sentinel API Server Starting...")
    print("📡 Real-time updates available at: http://localhost:8000/api/events")
    print("🌐 Dashboard API at: http://localhost:8000/api/")
    print("\nEndpoints:")
    print("  GET  /api/health")
    print("  GET  /api/findings")
    print("  GET  /api/incidents")
    print("  GET  /api/events (SSE)")
    print("  POST /api/scan")
    print("  POST /api/demo/simulate-attack")
    print("  POST /api/clear")
    print("\n✨ Ready for connections!\n")
    
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)

# Made with Bob
