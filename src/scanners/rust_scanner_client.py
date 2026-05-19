"""
Rust Scanner Client
Wrapper for calling the Rust scanner and normalizing findings
"""

import json
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RustScannerClient:
    """Client for interacting with the Rust scanner"""
    
    def __init__(self, rust_scanner_path: Optional[str] = None):
        """
        Initialize Rust scanner client
        
        Args:
            rust_scanner_path: Path to Rust scanner directory (default: ./rust-scanner)
        """
        if rust_scanner_path is None:
            # Default to rust-scanner directory in project root
            self.rust_scanner_path = Path(__file__).parent.parent.parent / "rust-scanner"
        else:
            self.rust_scanner_path = Path(rust_scanner_path)
        
        self.mock_findings_path = Path(__file__).parent.parent.parent / "contracts" / "sample_findings.json"
    
    def scan(self, paths: List[str], use_mock: bool = False) -> List[Dict[str, Any]]:
        """
        Scan paths for security findings
        
        Args:
            paths: List of paths to scan
            use_mock: If True, use mock findings instead of running Rust scanner
            
        Returns:
            List of normalized findings
        """
        if use_mock:
            logger.info("Using mock findings data")
            return self._load_mock_findings()
        
        try:
            logger.info(f"Running Rust scanner on paths: {paths}")
            findings = self._run_rust_scanner(paths)
            logger.info(f"Rust scanner found {len(findings)} findings")
            return findings
        except Exception as e:
            logger.warning(f"Rust scanner failed: {e}. Falling back to mock data.")
            return self._load_mock_findings()
    
    def _run_rust_scanner(self, paths: List[str]) -> List[Dict[str, Any]]:
        """Run the Rust scanner binary"""
        if not self.rust_scanner_path.exists():
            raise FileNotFoundError(f"Rust scanner not found at {self.rust_scanner_path}")
        
        # Build command
        cmd = ["cargo", "run", "--", "scan", "--path"] + paths
        
        # Run scanner
        result = subprocess.run(
            cmd,
            cwd=self.rust_scanner_path,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Rust scanner failed with code {result.returncode}: {result.stderr}")
        
        # Parse JSON output
        try:
            findings = json.loads(result.stdout)
            return self._normalize_findings(findings)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse Rust scanner output: {e}")
    
    def _load_mock_findings(self) -> List[Dict[str, Any]]:
        """Load mock findings for testing"""
        # Check if sample_findings.json exists and has content
        if self.mock_findings_path.exists():
            try:
                with open(self.mock_findings_path, 'r') as f:
                    content = f.read().strip()
                    if content:
                        findings = json.loads(content)
                        return self._normalize_findings(findings)
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Failed to load sample_findings.json: {e}")
        
        # Return hardcoded demo scenario findings
        logger.info("Using hardcoded demo scenario findings")
        return self._get_demo_scenario_findings()
    
    def _get_demo_scenario_findings(self) -> List[Dict[str, Any]]:
        """Get hardcoded findings for the demo scenario"""
        timestamp = datetime.now().isoformat() + "Z"
        
        return [
            {
                "finding_id": "FIND-001",
                "repo_name": "legacy-backend",
                "finding_type": "hardcoded_secret",
                "category": "secret_exposure",
                "severity_hint": "high",
                "source": "rust_scanner",
                "file": "legacy/old_export_api.py",
                "line": 12,
                "endpoint": "/api/v1/export-users",
                "database_table": None,
                "evidence": "Hardcoded API key detected in legacy export endpoint",
                "masked_value": "sk_test_****92fa",
                "timestamp": timestamp
            },
            {
                "finding_id": "FIND-002",
                "repo_name": "legacy-backend",
                "finding_type": "deprecated_api",
                "category": "legacy_api",
                "severity_hint": "medium",
                "source": "rust_scanner",
                "file": "legacy/old_export_api.py",
                "line": 8,
                "endpoint": "/api/v1/export-users",
                "database_table": None,
                "evidence": "Deprecated export endpoint still accessible",
                "masked_value": None,
                "timestamp": timestamp
            },
            {
                "finding_id": "FIND-003",
                "repo_name": "legacy-backend",
                "finding_type": "runtime_anomaly",
                "category": "runtime_behavior",
                "severity_hint": "medium",
                "source": "mock_data",
                "file": None,
                "line": None,
                "endpoint": "/api/v1/export-users",
                "database_table": None,
                "evidence": "Repeated suspicious access to deprecated endpoint (47 requests in 10 minutes)",
                "masked_value": None,
                "timestamp": timestamp
            },
            {
                "finding_id": "FIND-004",
                "repo_name": "legacy-backend",
                "finding_type": "database_anomaly",
                "category": "database_activity",
                "severity_hint": "high",
                "source": "mock_data",
                "file": None,
                "line": None,
                "endpoint": None,
                "database_table": "users",
                "evidence": "Abnormal read spike on users table (2,847 rows read in 5 minutes)",
                "masked_value": None,
                "timestamp": timestamp
            },
            {
                "finding_id": "FIND-005",
                "repo_name": "infra-config",
                "finding_type": "infrastructure_risk",
                "category": "infrastructure",
                "severity_hint": "medium",
                "source": "rust_scanner",
                "file": "gateway.yml",
                "line": 23,
                "endpoint": "/api/v1/export-users",
                "database_table": None,
                "evidence": "Gateway configuration still routes to deprecated export endpoint",
                "masked_value": None,
                "timestamp": timestamp
            }
        ]
    
    def _normalize_findings(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize findings to the shared Finding JSON format
        
        Args:
            findings: Raw findings from scanner
            
        Returns:
            Normalized findings
        """
        normalized = []
        
        for finding in findings:
            # Ensure all required fields exist
            normalized_finding = {
                "finding_id": finding.get("finding_id", f"FIND-{len(normalized)+1:03d}"),
                "repo_name": finding.get("repo_name", "unknown"),
                "finding_type": finding.get("finding_type", "unknown"),
                "category": finding.get("category", "unknown"),
                "severity_hint": finding.get("severity_hint", "medium").lower(),
                "source": finding.get("source", "rust_scanner"),
                "file": finding.get("file"),
                "line": finding.get("line"),
                "endpoint": finding.get("endpoint"),
                "database_table": finding.get("database_table"),
                "evidence": finding.get("evidence", ""),
                "masked_value": finding.get("masked_value"),
                "timestamp": finding.get("timestamp", datetime.now().isoformat() + "Z")
            }
            
            # Ensure severity is lowercase
            normalized_finding["severity_hint"] = normalized_finding["severity_hint"].lower()
            
            normalized.append(normalized_finding)
        
        return normalized
    
    def check_rust_scanner_available(self) -> bool:
        """Check if Rust scanner is available"""
        try:
            result = subprocess.run(
                ["cargo", "--version"],
                cwd=self.rust_scanner_path,
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False


# Made with Bob