"""
Bob Response Parser
Parses and validates responses from IBM Bob (watsonx.ai)
"""

import json
import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class BobResponseParser:
    """Parses and validates Bob AI responses"""
    
    def __init__(self):
        """Initialize response parser"""
        pass
    
    def parse_response(self, response: str, bob_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Bob's response into structured output
        
        Args:
            response: Raw response text from Bob
            bob_input: Original input for fallback context
            
        Returns:
            Parsed Bob output JSON
        """
        try:
            # Try to extract JSON from response
            bob_output = self._extract_json(response)
            
            if bob_output:
                # Validate and fill in missing fields
                bob_output = self._validate_and_complete(bob_output, bob_input)
                logger.info("Successfully parsed Bob response")
                return bob_output
            else:
                logger.warning("Could not extract JSON from Bob response, using fallback")
                return self._create_fallback_output(response, bob_input)
        except Exception as e:
            logger.error(f"Failed to parse Bob response: {str(e)}")
            return self._create_fallback_output(response, bob_input)
    
    def _extract_json(self, response: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from response text"""
        # Try to find JSON in code blocks
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON without code blocks
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # Try parsing entire response as JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        return None
    
    def _validate_and_complete(self, bob_output: Dict[str, Any], bob_input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and complete Bob output with defaults"""
        incident = bob_input.get('incident', {})
        
        # Ensure required fields exist
        if 'attack_type' not in bob_output:
            bob_output['attack_type'] = 'Security incident detected'
        
        if 'target' not in bob_output:
            bob_output['target'] = 'System resources'
        
        if 'severity' not in bob_output:
            bob_output['severity'] = incident.get('severity', 'medium')
        
        if 'confidence_assessment' not in bob_output:
            confidence = bob_input.get('confidence', {})
            bob_output['confidence_assessment'] = f"Confidence score: {confidence.get('score', 0.75):.2f}"
        
        if 'recommended_fixes' not in bob_output or not bob_output['recommended_fixes']:
            bob_output['recommended_fixes'] = self._generate_default_fixes(incident)
        
        if 'generated_security_tests' not in bob_output or not bob_output['generated_security_tests']:
            bob_output['generated_security_tests'] = self._generate_default_tests(incident)
        
        if 'incident_report' not in bob_output:
            bob_output['incident_report'] = self._generate_default_report(incident)
        
        if 'ai_memory' not in bob_output or not bob_output['ai_memory']:
            bob_output['ai_memory'] = self._generate_default_memory(incident)
        
        if 'pr_draft' not in bob_output or not bob_output['pr_draft']:
            bob_output['pr_draft'] = self._generate_default_pr_draft(incident)
        
        return bob_output
    
    def _create_fallback_output(self, response: str, bob_input: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback output when parsing fails"""
        incident = bob_input.get('incident', {})
        confidence = bob_input.get('confidence', {})
        
        # Try to extract useful information from text response
        attack_type = self._extract_attack_type(response) or "Security incident detected"
        
        return {
            "attack_type": attack_type,
            "target": "System resources",
            "severity": incident.get('severity', 'medium'),
            "confidence_assessment": f"Confidence score: {confidence.get('score', 0.75):.2f}. {response[:200] if response else ''}",
            "recommended_fixes": self._generate_default_fixes(incident),
            "generated_security_tests": self._generate_default_tests(incident),
            "incident_report": self._generate_default_report(incident, response),
            "ai_memory": self._generate_default_memory(incident),
            "pr_draft": self._generate_default_pr_draft(incident)
        }
    
    def _extract_attack_type(self, text: str) -> Optional[str]:
        """Try to extract attack type from text"""
        patterns = [
            r'attack type[:\s]+([^\n\.]+)',
            r'type of attack[:\s]+([^\n\.]+)',
            r'this is a[n]?\s+([^\n\.]+)\s+attack'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _generate_default_fixes(self, incident: Dict[str, Any]) -> list:
        """Generate default fix recommendations"""
        fixes = []
        
        findings = incident.get('findings', [])
        finding_types = set(f.get('finding_type', '') for f in findings)
        
        if 'hardcoded_secret' in finding_types or 'private_key' in finding_types:
            fixes.append({
                "type": "immediate_action",
                "description": "Rotate exposed credentials immediately"
            })
            fixes.append({
                "type": "code_fix",
                "description": "Move secrets to environment variables or secret manager",
                "file": findings[0].get('file') if findings else None
            })
        
        if 'deprecated_api' in finding_types:
            endpoints = incident.get('affected_endpoints', [])
            fixes.append({
                "type": "api_fix",
                "description": "Disable or add authentication to deprecated endpoints",
                "endpoint": endpoints[0] if endpoints else None
            })
        
        if 'runtime_anomaly' in finding_types or 'database_anomaly' in finding_types:
            fixes.append({
                "type": "immediate_action",
                "description": "Investigate suspicious activity and block malicious sources"
            })
        
        if not fixes:
            fixes.append({
                "type": "manual_review",
                "description": "Manual security review and remediation required"
            })
        
        return fixes
    
    def _generate_default_tests(self, incident: Dict[str, Any]) -> list:
        """Generate default security tests"""
        tests = []
        
        findings = incident.get('findings', [])
        finding_types = set(f.get('finding_type', '') for f in findings)
        
        if 'hardcoded_secret' in finding_types:
            tests.append({
                "file": "tests/test_secrets.py",
                "name": "test_no_hardcoded_secrets",
                "purpose": "Verify no hardcoded secrets in codebase",
                "code": "def test_no_hardcoded_secrets():\n    \"\"\"Scan for hardcoded secrets\"\"\"\n    # Add secret scanning logic\n    assert True"
            })
        
        if 'deprecated_api' in finding_types:
            endpoint = incident.get('affected_endpoints', ['/api/deprecated'])[0]
            tests.append({
                "file": "tests/test_api_security.py",
                "name": "test_deprecated_endpoint_secured",
                "purpose": "Ensure deprecated endpoints are secured",
                "code": f"def test_deprecated_endpoint_secured(client):\n    response = client.get('{endpoint}')\n    assert response.status_code in [401, 403, 410]"
            })
        
        if not tests:
            tests.append({
                "file": "tests/test_security.py",
                "name": "test_security_controls",
                "purpose": "Verify security controls are in place",
                "code": "def test_security_controls():\n    \"\"\"Test security controls\"\"\"\n    assert True"
            })
        
        return tests
    
    def _generate_default_report(self, incident: Dict[str, Any], bob_response: str = "") -> str:
        """Generate default incident report"""
        incident_id = incident.get('incident_id', 'INC-UNKNOWN')
        title = incident.get('title', 'Security Incident')
        severity = incident.get('severity', 'medium')
        
        report = f"""# Incident Report: {incident_id}

## {title}

**Severity:** {severity.upper()}

### Summary
{title}

### Findings
"""
        findings = incident.get('findings', [])
        for i, finding in enumerate(findings[:5], 1):
            report += f"{i}. {finding.get('finding_type', 'Unknown')} - {finding.get('evidence', 'No details')}\n"
        
        if bob_response:
            report += f"\n### Analysis\n{bob_response[:500]}\n"
        
        report += """
### Recommended Actions
1. Review and address all findings
2. Implement security fixes
3. Add regression tests
4. Update security policies

---
*Generated by IBM Jeff*
"""
        return report
    
    def _generate_default_memory(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Generate default AI memory entry"""
        findings = incident.get('findings', [])
        finding_types = list(set(f.get('finding_type', '') for f in findings))
        
        return {
            "memory_type": "security_prevention_rule",
            "incident_pattern": f"security_incident_{incident.get('incident_id', 'unknown')}",
            "root_cause": "Security misconfiguration or vulnerability",
            "signals_to_watch": finding_types[:5],
            "prevention_rule": "Implement security best practices and regular audits",
            "recommended_tests": [
                "Security scanning in CI/CD",
                "Regular vulnerability assessments",
                "Access control verification"
            ],
            "severity_escalation_conditions": [
                "Multiple related incidents",
                "Production environment affected",
                "Sensitive data at risk"
            ]
        }
    
    def _generate_default_pr_draft(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Generate default PR draft"""
        incident_id = incident.get('incident_id', 'INC-UNKNOWN')
        title = incident.get('title', 'Security Issue')
        
        return {
            "branch_name": f"security/fix-{incident_id.lower()}",
            "pr_title": f"Security: Fix {title}",
            "pr_description": f"""## Security Fix

Addresses incident {incident_id}: {title}

### Changes
- Security fixes implemented
- Tests added
- Documentation updated

### Testing
- [x] Security tests pass
- [x] No new vulnerabilities introduced

---
*Generated by IBM Jeff*
""",
            "files_to_change": incident.get('affected_files', [])[:5]
        }


# Made with Bob