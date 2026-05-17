#!/usr/bin/env python3
"""
Mock Dataset Generator for Security Incidents
Generates random security incidents for testing the BOB system
Each run generates ONE random incident with associated findings
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid


class MockIncidentGenerator:
    """Generates realistic mock security incidents"""
    
    def __init__(self):
        self.incident_templates = [
            self._generate_credential_leak_incident,
            self._generate_sql_injection_incident,
            self._generate_command_injection_incident,
            self._generate_data_exfiltration_incident,
            self._generate_weak_auth_incident,
            self._generate_debug_exposure_incident,
            self._generate_path_traversal_incident,
            self._generate_cors_misconfiguration_incident,
            self._generate_rate_limit_abuse_incident,
            self._generate_sensitive_data_logging_incident,
        ]
        
        self.repos = ["legacy-backend", "frontend-app", "infra-config", "payment-service", "user-service"]
        self.severities = ["critical", "high", "medium", "low"]
        
    def generate_random_incident(self) -> Dict[str, Any]:
        """Generate one random incident"""
        # Randomly select an incident type
        incident_generator = random.choice(self.incident_templates)
        return incident_generator()
    
    def _generate_timestamp(self, minutes_ago: int = 0) -> str:
        """Generate ISO timestamp"""
        time = datetime.utcnow() - timedelta(minutes=minutes_ago)
        return time.isoformat() + "Z"
    
    def _generate_finding_id(self) -> str:
        """Generate unique finding ID"""
        return f"FIND-{random.randint(1000, 9999)}"
    
    def _generate_incident_id(self) -> str:
        """Generate unique incident ID"""
        return f"INC-{random.randint(1000, 9999)}"
    
    def _generate_credential_leak_incident(self) -> Dict[str, Any]:
        """Generate credential leakage incident"""
        incident_id = self._generate_incident_id()
        repo = random.choice(self.repos)
        
        api_keys = [
            "sk_test_EXAMPLE_FAKE_KEY_FOR_TESTING",
            "AKIAIOSFODNN7EXAMPLE",
            "ghp_EXAMPLE_FAKE_GITHUB_TOKEN_FOR_TESTING",
            "xoxb-EXAMPLE-FAKE-SLACK-TOKEN-FOR-TESTING"
        ]
        
        files = [
            "config/secrets.py",
            "src/auth/credentials.js",
            "deploy/env_vars.sh",
            ".env.production",
            "api/keys.yaml"
        ]
        
        endpoints = [
            "/api/v1/export-users",
            "/api/v2/admin/data",
            "/api/v3/backup",
            "/internal/debug"
        ]
        
        api_key = random.choice(api_keys)
        masked_key = api_key[:8] + "****" + api_key[-4:]
        file = random.choice(files)
        endpoint = random.choice(endpoints)
        
        findings = [
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "hardcoded_secret",
                "category": "secret_exposure",
                "severity_hint": "critical",
                "source": "rust_scanner",
                "file": file,
                "line": random.randint(10, 200),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": f"Hardcoded API key detected: {masked_key}",
                "masked_value": masked_key,
                "timestamp": self._generate_timestamp(10)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "deprecated_api",
                "category": "legacy_api",
                "severity_hint": "high",
                "source": "python_analyzer",
                "file": file,
                "line": random.randint(10, 200),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": "Deprecated API endpoint still accessible",
                "masked_value": None,
                "timestamp": self._generate_timestamp(8)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "runtime_anomaly",
                "category": "runtime_behavior",
                "severity_hint": "high",
                "source": "mock_data",
                "file": None,
                "line": None,
                "endpoint": endpoint,
                "database_table": None,
                "evidence": f"Suspicious access pattern: {random.randint(50, 200)} requests in {random.randint(5, 15)} minutes",
                "masked_value": None,
                "timestamp": self._generate_timestamp(5)
            }
        ]
        
        return {
            "incident_id": incident_id,
            "title": f"Credential leakage through exposed {endpoint} endpoint",
            "severity": "critical",
            "severity_level": 5,
            "confidence_score": round(random.uniform(0.75, 0.95), 2),
            "confidence_reasons": [
                "Hardcoded API key found in source code",
                "Deprecated endpoint is still reachable",
                "Suspicious access patterns detected",
                "Multiple security layers compromised"
            ],
            "confidence_limitations": [
                "Unable to verify actual data exfiltration",
                "Analysis based on available logs only"
            ],
            "affected_repos": [repo],
            "affected_files": [file],
            "affected_endpoints": [endpoint],
            "affected_database_tables": [],
            "findings": findings,
            "finding_count": len(findings),
            "correlation_type": "attack_chain",
            "description": f"Detected credential exposure in {repo} with suspicious access patterns",
            "timestamp": self._generate_timestamp(),
            "attack_path": self._generate_attack_path(findings, "credential_leak")
        }
    
    def _generate_sql_injection_incident(self) -> Dict[str, Any]:
        """Generate SQL injection incident"""
        incident_id = self._generate_incident_id()
        repo = random.choice(self.repos)
        
        endpoints = ["/api/v1/users", "/api/v2/search", "/api/v1/admin/users", "/api/v3/export"]
        tables = ["users", "orders", "payments", "sessions", "products"]
        
        endpoint = random.choice(endpoints)
        table = random.choice(tables)
        file = f"api/{endpoint.split('/')[-1]}.py"
        
        findings = [
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "sql_injection",
                "category": "injection_vulnerability",
                "severity_hint": "critical",
                "source": "rust_scanner",
                "file": file,
                "line": random.randint(20, 150),
                "endpoint": endpoint,
                "database_table": table,
                "evidence": f"Unsanitized user input in SQL query: SELECT * FROM {table} WHERE id = {{user_input}}",
                "masked_value": None,
                "timestamp": self._generate_timestamp(12)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "runtime_anomaly",
                "category": "runtime_behavior",
                "severity_hint": "high",
                "source": "mock_data",
                "file": None,
                "line": None,
                "endpoint": endpoint,
                "database_table": None,
                "evidence": f"SQL injection attempt detected: {random.randint(15, 50)} malicious queries",
                "masked_value": None,
                "timestamp": self._generate_timestamp(8)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "database_anomaly",
                "category": "database_activity",
                "severity_hint": "critical",
                "source": "mock_data",
                "file": None,
                "line": None,
                "endpoint": None,
                "database_table": table,
                "evidence": f"Abnormal {table} table access: {random.randint(1000, 5000)} rows read in {random.randint(2, 10)} minutes",
                "masked_value": None,
                "timestamp": self._generate_timestamp(5)
            }
        ]
        
        return {
            "incident_id": incident_id,
            "title": f"SQL injection vulnerability in {endpoint} endpoint",
            "severity": "critical",
            "severity_level": 5,
            "confidence_score": round(random.uniform(0.80, 0.95), 2),
            "confidence_reasons": [
                "SQL injection vulnerability confirmed in code",
                "Active exploitation attempts detected",
                "Database anomaly correlates with attack",
                "No input sanitization present"
            ],
            "confidence_limitations": [
                "Cannot confirm data exfiltration",
                "Limited visibility into attacker actions"
            ],
            "affected_repos": [repo],
            "affected_files": [file],
            "affected_endpoints": [endpoint],
            "affected_database_tables": [table],
            "findings": findings,
            "finding_count": len(findings),
            "correlation_type": "attack_chain",
            "description": f"SQL injection vulnerability actively exploited in {endpoint}",
            "timestamp": self._generate_timestamp(),
            "attack_path": self._generate_attack_path(findings, "sql_injection")
        }
    
    def _generate_command_injection_incident(self) -> Dict[str, Any]:
        """Generate command injection incident"""
        incident_id = self._generate_incident_id()
        repo = random.choice(self.repos)
        
        endpoints = ["/api/v3/execute", "/api/v3/backup", "/api/v2/deploy", "/admin/shell"]
        file = "api/admin_commands.py"
        endpoint = random.choice(endpoints)
        
        findings = [
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "command_injection",
                "category": "injection_vulnerability",
                "severity_hint": "critical",
                "source": "rust_scanner",
                "file": file,
                "line": random.randint(50, 200),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": "Unsanitized command execution: subprocess.run(user_input, shell=True)",
                "masked_value": None,
                "timestamp": self._generate_timestamp(15)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "runtime_anomaly",
                "category": "runtime_behavior",
                "severity_hint": "critical",
                "source": "mock_data",
                "file": None,
                "line": None,
                "endpoint": endpoint,
                "database_table": None,
                "evidence": f"Suspicious system commands executed: {random.randint(10, 30)} shell commands",
                "masked_value": None,
                "timestamp": self._generate_timestamp(10)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "authentication_bypass",
                "category": "authentication",
                "severity_hint": "high",
                "source": "python_analyzer",
                "file": file,
                "line": random.randint(10, 50),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": "No authentication check before command execution",
                "masked_value": None,
                "timestamp": self._generate_timestamp(14)
            }
        ]
        
        return {
            "incident_id": incident_id,
            "title": f"Command injection vulnerability in {endpoint}",
            "severity": "critical",
            "severity_level": 5,
            "confidence_score": round(random.uniform(0.85, 0.98), 2),
            "confidence_reasons": [
                "Command injection vulnerability confirmed",
                "No authentication on dangerous endpoint",
                "Active exploitation detected",
                "System-level access possible"
            ],
            "confidence_limitations": [
                "Cannot determine full extent of compromise"
            ],
            "affected_repos": [repo],
            "affected_files": [file],
            "affected_endpoints": [endpoint],
            "affected_database_tables": [],
            "findings": findings,
            "finding_count": len(findings),
            "correlation_type": "attack_chain",
            "description": f"Critical command injection vulnerability with active exploitation",
            "timestamp": self._generate_timestamp(),
            "attack_path": self._generate_attack_path(findings, "command_injection")
        }
    
    def _generate_data_exfiltration_incident(self) -> Dict[str, Any]:
        """Generate data exfiltration incident"""
        incident_id = self._generate_incident_id()
        repos = random.sample(self.repos, 2)
        
        tables = ["users", "credit_cards", "personal_info", "transactions"]
        table = random.choice(tables)
        endpoint = "/api/v3/export"
        
        findings = [
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repos[0],
                "finding_type": "sensitive_data_exposure",
                "category": "data_exposure",
                "severity_hint": "critical",
                "source": "python_analyzer",
                "file": "api/export.py",
                "line": random.randint(30, 100),
                "endpoint": endpoint,
                "database_table": table,
                "evidence": f"Endpoint returns sensitive {table} data without proper authorization",
                "masked_value": None,
                "timestamp": self._generate_timestamp(20)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repos[0],
                "finding_type": "runtime_anomaly",
                "category": "runtime_behavior",
                "severity_hint": "critical",
                "source": "mock_data",
                "file": None,
                "line": None,
                "endpoint": endpoint,
                "database_table": None,
                "evidence": f"Massive data export: {random.randint(10000, 50000)} records in {random.randint(5, 15)} minutes",
                "masked_value": None,
                "timestamp": self._generate_timestamp(15)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repos[0],
                "finding_type": "database_anomaly",
                "category": "database_activity",
                "severity_hint": "critical",
                "source": "mock_data",
                "file": None,
                "line": None,
                "endpoint": None,
                "database_table": table,
                "evidence": f"{table} table: {random.randint(5000, 20000)} rows read, {random.randint(10, 50)}x normal baseline",
                "masked_value": None,
                "timestamp": self._generate_timestamp(12)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repos[1],
                "finding_type": "infrastructure_risk",
                "category": "infrastructure",
                "severity_hint": "high",
                "source": "rust_scanner",
                "file": "gateway.yml",
                "line": random.randint(20, 80),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": "Export endpoint exposed without rate limiting",
                "masked_value": None,
                "timestamp": self._generate_timestamp(18)
            }
        ]
        
        return {
            "incident_id": incident_id,
            "title": f"Mass data exfiltration from {table} table",
            "severity": "critical",
            "severity_level": 5,
            "confidence_score": round(random.uniform(0.82, 0.94), 2),
            "confidence_reasons": [
                "Massive data export detected",
                "Database read spike correlates with API calls",
                "No rate limiting on export endpoint",
                "Sensitive data exposed without authorization",
                "Multiple repositories affected"
            ],
            "confidence_limitations": [
                "Cannot confirm destination of exported data",
                "Limited network traffic visibility"
            ],
            "affected_repos": repos,
            "affected_files": ["api/export.py", "gateway.yml"],
            "affected_endpoints": [endpoint],
            "affected_database_tables": [table],
            "findings": findings,
            "finding_count": len(findings),
            "correlation_type": "attack_chain",
            "description": f"Large-scale data exfiltration detected from {table} table",
            "timestamp": self._generate_timestamp(),
            "attack_path": self._generate_attack_path(findings, "data_exfiltration")
        }
    
    def _generate_weak_auth_incident(self) -> Dict[str, Any]:
        """Generate weak authentication incident"""
        incident_id = self._generate_incident_id()
        repo = random.choice(self.repos)
        
        endpoint = random.choice(["/api/v1/legacy/auth", "/api/v2/login", "/admin/auth"])
        
        findings = [
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "weak_authentication",
                "category": "authentication",
                "severity_hint": "high",
                "source": "python_analyzer",
                "file": "auth/legacy_auth.py",
                "line": random.randint(20, 100),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": "Weak password check: hardcoded credentials (admin/admin123)",
                "masked_value": "admin/****123",
                "timestamp": self._generate_timestamp(25)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "credential_logging",
                "category": "data_exposure",
                "severity_hint": "high",
                "source": "rust_scanner",
                "file": "auth/legacy_auth.py",
                "line": random.randint(20, 100),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": "Credentials logged in plaintext: logger.info(f'Login: {username}:{password}')",
                "masked_value": None,
                "timestamp": self._generate_timestamp(24)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "runtime_anomaly",
                "category": "runtime_behavior",
                "severity_hint": "medium",
                "source": "mock_data",
                "file": None,
                "line": None,
                "endpoint": endpoint,
                "database_table": None,
                "evidence": f"Brute force attempt: {random.randint(100, 500)} failed login attempts",
                "masked_value": None,
                "timestamp": self._generate_timestamp(20)
            }
        ]
        
        return {
            "incident_id": incident_id,
            "title": f"Weak authentication mechanism in {endpoint}",
            "severity": "high",
            "severity_level": 4,
            "confidence_score": round(random.uniform(0.75, 0.90), 2),
            "confidence_reasons": [
                "Hardcoded credentials found",
                "Credentials logged in plaintext",
                "Brute force attempts detected",
                "No rate limiting on auth endpoint"
            ],
            "confidence_limitations": [
                "Cannot confirm successful unauthorized access"
            ],
            "affected_repos": [repo],
            "affected_files": ["auth/legacy_auth.py"],
            "affected_endpoints": [endpoint],
            "affected_database_tables": [],
            "findings": findings,
            "finding_count": len(findings),
            "correlation_type": "vulnerability_cluster",
            "description": f"Weak authentication with credential exposure and brute force attempts",
            "timestamp": self._generate_timestamp(),
            "attack_path": self._generate_attack_path(findings, "weak_auth")
        }
    
    def _generate_debug_exposure_incident(self) -> Dict[str, Any]:
        """Generate debug endpoint exposure incident"""
        incident_id = self._generate_incident_id()
        repo = random.choice(self.repos)
        
        endpoint = "/api/v3/debug"
        
        findings = [
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "debug_endpoint",
                "category": "configuration",
                "severity_hint": "critical",
                "source": "rust_scanner",
                "file": "api/debug.py",
                "line": random.randint(10, 50),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": "Debug endpoint exposed in production: returns environment variables",
                "masked_value": None,
                "timestamp": self._generate_timestamp(30)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "authentication_bypass",
                "category": "authentication",
                "severity_hint": "critical",
                "source": "python_analyzer",
                "file": "api/debug.py",
                "line": random.randint(10, 50),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": "No authentication required for debug endpoint",
                "masked_value": None,
                "timestamp": self._generate_timestamp(29)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "runtime_anomaly",
                "category": "runtime_behavior",
                "severity_hint": "high",
                "source": "mock_data",
                "file": None,
                "line": None,
                "endpoint": endpoint,
                "database_table": None,
                "evidence": f"Debug endpoint accessed {random.randint(20, 100)} times from external IPs",
                "masked_value": None,
                "timestamp": self._generate_timestamp(25)
            }
        ]
        
        return {
            "incident_id": incident_id,
            "title": "Debug endpoint exposing sensitive configuration",
            "severity": "critical",
            "severity_level": 5,
            "confidence_score": round(random.uniform(0.88, 0.96), 2),
            "confidence_reasons": [
                "Debug endpoint confirmed in production",
                "No authentication protection",
                "Exposes environment variables and secrets",
                "External access detected"
            ],
            "confidence_limitations": [
                "Cannot determine what data was accessed"
            ],
            "affected_repos": [repo],
            "affected_files": ["api/debug.py"],
            "affected_endpoints": [endpoint],
            "affected_database_tables": [],
            "findings": findings,
            "finding_count": len(findings),
            "correlation_type": "vulnerability_cluster",
            "description": "Production debug endpoint exposing sensitive configuration data",
            "timestamp": self._generate_timestamp(),
            "attack_path": self._generate_attack_path(findings, "debug_exposure")
        }
    
    def _generate_path_traversal_incident(self) -> Dict[str, Any]:
        """Generate path traversal incident"""
        incident_id = self._generate_incident_id()
        repo = random.choice(self.repos)
        
        endpoints = ["/api/v3/logs", "/api/v3/upload", "/files/download"]
        endpoint = random.choice(endpoints)
        
        findings = [
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "path_traversal",
                "category": "injection_vulnerability",
                "severity_hint": "high",
                "source": "rust_scanner",
                "file": "api/file_handler.py",
                "line": random.randint(30, 120),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": "Unsanitized file path: open(f'/var/log/{user_input}')",
                "masked_value": None,
                "timestamp": self._generate_timestamp(18)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "runtime_anomaly",
                "category": "runtime_behavior",
                "severity_hint": "high",
                "source": "mock_data",
                "file": None,
                "line": None,
                "endpoint": endpoint,
                "database_table": None,
                "evidence": f"Path traversal attempts: {random.randint(15, 60)} requests with '../' patterns",
                "masked_value": None,
                "timestamp": self._generate_timestamp(15)
            }
        ]
        
        return {
            "incident_id": incident_id,
            "title": f"Path traversal vulnerability in {endpoint}",
            "severity": "high",
            "severity_level": 4,
            "confidence_score": round(random.uniform(0.78, 0.92), 2),
            "confidence_reasons": [
                "Path traversal vulnerability confirmed",
                "Active exploitation attempts detected",
                "No input sanitization"
            ],
            "confidence_limitations": [
                "Cannot confirm which files were accessed",
                "Limited file system monitoring"
            ],
            "affected_repos": [repo],
            "affected_files": ["api/file_handler.py"],
            "affected_endpoints": [endpoint],
            "affected_database_tables": [],
            "findings": findings,
            "finding_count": len(findings),
            "correlation_type": "attack_chain",
            "description": f"Path traversal vulnerability with active exploitation",
            "timestamp": self._generate_timestamp(),
            "attack_path": self._generate_attack_path(findings, "path_traversal")
        }
    
    def _generate_cors_misconfiguration_incident(self) -> Dict[str, Any]:
        """Generate CORS misconfiguration incident"""
        incident_id = self._generate_incident_id()
        repo = random.choice(self.repos)
        
        findings = [
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "cors_misconfiguration",
                "category": "configuration",
                "severity_hint": "medium",
                "source": "rust_scanner",
                "file": "api/middleware.py",
                "line": random.randint(10, 80),
                "endpoint": None,
                "database_table": None,
                "evidence": "CORS allows all origins: Access-Control-Allow-Origin: *",
                "masked_value": None,
                "timestamp": self._generate_timestamp(22)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "sensitive_data_exposure",
                "category": "data_exposure",
                "severity_hint": "high",
                "source": "python_analyzer",
                "file": "api/user_api.py",
                "line": random.randint(50, 150),
                "endpoint": "/api/v3/users",
                "database_table": "users",
                "evidence": "API returns sensitive user data (SSN, credit cards) with permissive CORS",
                "masked_value": None,
                "timestamp": self._generate_timestamp(20)
            }
        ]
        
        return {
            "incident_id": incident_id,
            "title": "CORS misconfiguration exposing sensitive data",
            "severity": "high",
            "severity_level": 4,
            "confidence_score": round(random.uniform(0.70, 0.85), 2),
            "confidence_reasons": [
                "Permissive CORS policy confirmed",
                "Sensitive data accessible via API",
                "No origin restrictions"
            ],
            "confidence_limitations": [
                "Cannot confirm actual cross-origin attacks"
            ],
            "affected_repos": [repo],
            "affected_files": ["api/middleware.py", "api/user_api.py"],
            "affected_endpoints": ["/api/v3/users"],
            "affected_database_tables": ["users"],
            "findings": findings,
            "finding_count": len(findings),
            "correlation_type": "vulnerability_cluster",
            "description": "Permissive CORS policy allows cross-origin access to sensitive data",
            "timestamp": self._generate_timestamp(),
            "attack_path": self._generate_attack_path(findings, "cors_misconfiguration")
        }
    
    def _generate_rate_limit_abuse_incident(self) -> Dict[str, Any]:
        """Generate rate limiting abuse incident"""
        incident_id = self._generate_incident_id()
        repo = random.choice(self.repos)
        
        endpoints = ["/api/v2/password-reset", "/api/v1/legacy/auth", "/api/v3/export"]
        endpoint = random.choice(endpoints)
        
        findings = [
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "missing_rate_limit",
                "category": "configuration",
                "severity_hint": "medium",
                "source": "python_analyzer",
                "file": "api/auth.py",
                "line": random.randint(20, 100),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": f"No rate limiting on {endpoint}",
                "masked_value": None,
                "timestamp": self._generate_timestamp(35)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "runtime_anomaly",
                "category": "runtime_behavior",
                "severity_hint": "high",
                "source": "mock_data",
                "file": None,
                "line": None,
                "endpoint": endpoint,
                "database_table": None,
                "evidence": f"Abuse detected: {random.randint(500, 2000)} requests in {random.randint(1, 5)} minutes from single IP",
                "masked_value": None,
                "timestamp": self._generate_timestamp(30)
            }
        ]
        
        return {
            "incident_id": incident_id,
            "title": f"Rate limiting abuse on {endpoint}",
            "severity": "medium",
            "severity_level": 3,
            "confidence_score": round(random.uniform(0.72, 0.88), 2),
            "confidence_reasons": [
                "No rate limiting configured",
                "Abnormal request volume detected",
                "Single source IP identified"
            ],
            "confidence_limitations": [
                "Cannot determine attacker intent",
                "May be legitimate traffic spike"
            ],
            "affected_repos": [repo],
            "affected_files": ["api/auth.py"],
            "affected_endpoints": [endpoint],
            "affected_database_tables": [],
            "findings": findings,
            "finding_count": len(findings),
            "correlation_type": "vulnerability_cluster",
            "description": f"Endpoint abuse due to missing rate limiting",
            "timestamp": self._generate_timestamp(),
            "attack_path": self._generate_attack_path(findings, "rate_limit_abuse")
        }
    
    def _generate_sensitive_data_logging_incident(self) -> Dict[str, Any]:
        """Generate sensitive data logging incident"""
        incident_id = self._generate_incident_id()
        repo = random.choice(self.repos)
        
        endpoints = ["/api/v2/payments", "/api/v1/legacy/auth", "/api/v3/users"]
        endpoint = random.choice(endpoints)
        
        findings = [
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "sensitive_data_logging",
                "category": "data_exposure",
                "severity_hint": "high",
                "source": "rust_scanner",
                "file": "api/payment.py",
                "line": random.randint(40, 150),
                "endpoint": endpoint,
                "database_table": None,
                "evidence": "Sensitive data logged: logger.info(f'Payment: {card_number}, CVV: {cvv}')",
                "masked_value": None,
                "timestamp": self._generate_timestamp(28)
            },
            {
                "finding_id": self._generate_finding_id(),
                "repo_name": repo,
                "finding_type": "infrastructure_risk",
                "category": "infrastructure",
                "severity_hint": "medium",
                "source": "rust_scanner",
                "file": "config/logging.yml",
                "line": random.randint(5, 30),
                "endpoint": None,
                "database_table": None,
                "evidence": "Logs stored without encryption in /var/log/app.log",
                "masked_value": None,
                "timestamp": self._generate_timestamp(26)
            }
        ]
        
        return {
            "incident_id": incident_id,
            "title": f"Sensitive data logged in plaintext",
            "severity": "high",
            "severity_level": 4,
            "confidence_score": round(random.uniform(0.80, 0.92), 2),
            "confidence_reasons": [
                "Sensitive data logging confirmed in code",
                "Logs stored unencrypted",
                "PCI/PII data exposed in logs"
            ],
            "confidence_limitations": [
                "Cannot determine who accessed logs"
            ],
            "affected_repos": [repo],
            "affected_files": ["api/payment.py", "config/logging.yml"],
            "affected_endpoints": [endpoint],
            "affected_database_tables": [],
            "findings": findings,
            "finding_count": len(findings),
            "correlation_type": "vulnerability_cluster",
            "description": "Sensitive payment/credential data logged in plaintext",
            "timestamp": self._generate_timestamp(),
            "attack_path": self._generate_attack_path(findings, "sensitive_logging")
        }
    
    def _generate_attack_path(self, findings: List[Dict], incident_type: str) -> Dict[str, Any]:
        """Generate attack path visualization data"""
        
        # Create nodes from findings
        nodes = []
        node_id_map = {}
        
        for i, finding in enumerate(findings):
            node_id = f"node_{i}"
            node_type = finding["category"].split("_")[0]
            
            node = {
                "id": node_id,
                "label": finding["finding_type"].replace("_", " ").title(),
                "type": node_type,
                "findings": [finding["finding_id"]],
                "evidence": [finding["evidence"]]
            }
            
            if finding.get("file"):
                node["file"] = finding["file"]
            if finding.get("endpoint"):
                node["endpoint"] = finding["endpoint"]
            if finding.get("database_table"):
                node["database_table"] = finding["database_table"]
            
            nodes.append(node)
            node_id_map[i] = node_id
        
        # Add impact node
        impact_node = {
            "id": "impact",
            "label": "Security Impact",
            "type": "impact"
        }
        nodes.append(impact_node)
        
        # Create edges
        edges = []
        for i in range(len(findings)):
            if i < len(findings) - 1:
                edges.append({
                    "from": node_id_map[i],
                    "to": node_id_map[i + 1],
                    "label": "leads to"
                })
            else:
                edges.append({
                    "from": node_id_map[i],
                    "to": "impact",
                    "label": "results in"
                })
        
        return {
            "nodes": nodes,
            "edges": edges
        }


def main():
    """Main function to generate and output a random incident"""
    generator = MockIncidentGenerator()
    incident = generator.generate_random_incident()
    
    # Pretty print the incident
    print(json.dumps(incident, indent=2))
    
    # Also save to file
    output_file = f"mock_incident_{incident['incident_id']}.json"
    with open(output_file, 'w') as f:
        json.dump(incident, f, indent=2)
    
    print(f"\n✅ Generated incident saved to: {output_file}", file=__import__('sys').stderr)
    print(f"📊 Incident Type: {incident['title']}", file=__import__('sys').stderr)
    print(f"🔴 Severity: {incident['severity']} (Level {incident['severity_level']})", file=__import__('sys').stderr)
    print(f"🔍 Findings: {incident['finding_count']}", file=__import__('sys').stderr)
    print(f"📈 Confidence: {incident['confidence_score']}", file=__import__('sys').stderr)


if __name__ == "__main__":
    main()

# Made with Bob
