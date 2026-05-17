"""
Data Normalization Utilities
Handles conversion between old and new data formats for findings and incidents
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


def normalize_finding(finding: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a finding to the standard format, handling both old and new schemas.
    
    Args:
        finding: Raw finding dictionary (may be old or new format)
        
    Returns:
        Normalized finding dictionary matching the current schema
    """
    # Handle both 'type' (old) and 'finding_type' (new)
    finding_type = finding.get("finding_type") or finding.get("type") or "unknown"
    
    # Ensure severity_hint is lowercase
    severity_hint = str(finding.get("severity_hint", "medium")).lower()
    
    return {
        "finding_id": finding.get("finding_id", f"FIND-{id(finding)}"),
        "repo_name": finding.get("repo_name", "unknown"),
        "finding_type": finding_type,
        "category": finding.get("category", "unknown"),
        "severity_hint": severity_hint,
        "source": finding.get("source", "unknown"),
        "file": finding.get("file"),
        "line": finding.get("line"),
        "endpoint": finding.get("endpoint"),
        "database_table": finding.get("database_table"),
        "evidence": finding.get("evidence", ""),
        "masked_value": finding.get("masked_value"),
        "timestamp": finding.get("timestamp", datetime.now().isoformat() + "Z")
    }


def normalize_findings(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize a list of findings.
    
    Args:
        findings: List of raw finding dictionaries
        
    Returns:
        List of normalized finding dictionaries
    """
    return [normalize_finding(f) for f in findings]


def normalize_severity(severity: Any) -> tuple[str, int]:
    """
    Normalize severity to both string and numeric level.
    Handles both old format (dict with 'level' and 'label') and new format (string).
    
    Args:
        severity: Severity value (string, dict, or int)
        
    Returns:
        Tuple of (severity_string, severity_level)
    """
    # Map severity strings to levels
    severity_map = {
        "info": 1,
        "low": 2,
        "medium": 3,
        "high": 4,
        "critical": 5
    }
    
    # Handle old format: {"level": 5, "label": "critical"}
    if isinstance(severity, dict):
        level = severity.get("level", 3)
        label = severity.get("label", "medium")
        return label.lower(), level
    
    # Handle new format: "critical" or severity_level: 5
    if isinstance(severity, str):
        severity_str = severity.lower()
        level = severity_map.get(severity_str, 3)
        return severity_str, level
    
    # Handle numeric level
    if isinstance(severity, int):
        level = max(1, min(5, severity))
        reverse_map = {v: k for k, v in severity_map.items()}
        severity_str = reverse_map.get(level, "medium")
        return severity_str, level
    
    # Default
    return "medium", 3


def normalize_incident(incident: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize an incident to the standard format.
    
    Args:
        incident: Raw incident dictionary
        
    Returns:
        Normalized incident dictionary
    """
    # Normalize severity
    severity_str, severity_level = normalize_severity(
        incident.get("severity", "medium")
    )
    
    # Normalize findings
    findings = incident.get("findings", [])
    normalized_findings = normalize_findings(findings)
    
    # Ensure related_memory exists
    related_memory = incident.get("related_memory", [])
    
    # Ensure attack_path exists
    attack_path = incident.get("attack_path", {"nodes": [], "edges": []})
    
    return {
        "incident_id": incident.get("incident_id", f"INC-{id(incident)}"),
        "title": incident.get("title", "Untitled Incident"),
        "severity": severity_str,
        "severity_level": severity_level,
        "confidence_score": incident.get("confidence_score", 0.5),
        "confidence_reasons": incident.get("confidence_reasons", []),
        "confidence_limitations": incident.get("confidence_limitations", []),
        "affected_repos": incident.get("affected_repos", []),
        "affected_files": incident.get("affected_files", []),
        "affected_endpoints": incident.get("affected_endpoints", []),
        "affected_database_tables": incident.get("affected_database_tables", []),
        "findings": normalized_findings,
        "attack_path": attack_path,
        "related_memory": related_memory,
        "timestamp": incident.get("timestamp", datetime.now().isoformat() + "Z")
    }


def safe_get_finding_type(finding: Dict[str, Any]) -> str:
    """
    Safely extract finding type from a finding, handling both old and new formats.
    
    Args:
        finding: Finding dictionary
        
    Returns:
        Finding type string
    """
    return finding.get("finding_type") or finding.get("type") or "unknown"


def safe_get_severity(incident_or_finding: Dict[str, Any]) -> tuple[str, int]:
    """
    Safely extract severity from an incident or finding.
    
    Args:
        incident_or_finding: Incident or finding dictionary
        
    Returns:
        Tuple of (severity_string, severity_level)
    """
    severity = incident_or_finding.get("severity") or incident_or_finding.get("severity_hint")
    return normalize_severity(severity)


def extract_finding_pattern(finding: Dict[str, Any]) -> str:
    """
    Extract a pattern string from a finding for memory/correlation purposes.
    
    Args:
        finding: Normalized finding dictionary
        
    Returns:
        Pattern string (e.g., "hardcoded_secret_in_legacy_api")
    """
    finding_type = safe_get_finding_type(finding)
    category = finding.get("category", "unknown")
    
    # Create a meaningful pattern
    if finding.get("endpoint"):
        return f"{finding_type}_in_{category}_endpoint"
    elif finding.get("database_table"):
        return f"{finding_type}_in_{category}_database"
    elif finding.get("file"):
        return f"{finding_type}_in_{category}_file"
    else:
        return f"{finding_type}_in_{category}"


def extract_incident_pattern(incident: Dict[str, Any]) -> str:
    """
    Extract a pattern string from an incident for memory purposes.
    
    Args:
        incident: Normalized incident dictionary
        
    Returns:
        Pattern string describing the incident
    """
    findings = incident.get("findings", [])
    if not findings:
        return "unknown_incident_pattern"
    
    # Get finding types
    finding_types = [safe_get_finding_type(f) for f in findings]
    finding_types = [ft for ft in finding_types if ft and ft != "unknown"]
    
    if not finding_types:
        return "unknown_incident_pattern"
    
    # Create pattern from finding types
    if len(finding_types) == 1:
        return f"{finding_types[0]}_incident"
    else:
        # Sort for consistency
        finding_types.sort()
        return "_and_".join(finding_types[:3])  # Limit to 3 types


# Made with Bob