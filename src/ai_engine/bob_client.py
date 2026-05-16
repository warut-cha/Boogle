"""
IBM Bob Client
Integrates with IBM watsonx.ai for AI-powered security analysis
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    from ibm_watsonx_ai import APIClient, Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    WATSONX_AVAILABLE = True
except ImportError:
    WATSONX_AVAILABLE = False
    logger.warning("IBM watsonx.ai SDK not available. Install with: pip install ibm-watsonx-ai")


class BobClient:
    """Client for IBM Bob (watsonx.ai) API"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Bob client
        
        Args:
            config: Bob configuration including API credentials
        """
        self.config = config
        self.mock_mode = config.get('mock_mode', False)
        # mock_mode works without the SDK; real mode requires it
        self.enabled = config.get('enabled', True) and (self.mock_mode or WATSONX_AVAILABLE)
        
        # Model configuration
        self.model_id = config.get('model_id', 'ibm/granite-13b-chat-v2')
        self.project_id = config.get('project_id', os.getenv('WATSONX_PROJECT_ID'))
        self.api_key = config.get('api_key', os.getenv('WATSONX_API_KEY'))
        self.url = config.get('url', os.getenv('WATSONX_URL', 'https://us-south.ml.cloud.ibm.com'))
        
        # Generation parameters
        self.max_tokens = config.get('max_tokens', 2000)
        self.temperature = config.get('temperature', 0.7)
        self.top_p = config.get('top_p', 0.9)
        self.top_k = config.get('top_k', 50)
        
        self.client = None
        self.model = None
        
        if not self.mock_mode and self.enabled:
            self._init_client()
    
    def _init_client(self):
        """Initialize watsonx.ai client"""
        if not self.api_key or not self.project_id:
            logger.warning("IBM watsonx.ai credentials not configured. Set WATSONX_API_KEY and WATSONX_PROJECT_ID")
            self.enabled = False
            return
        
        try:
            # Create credentials
            credentials = Credentials(
                api_key=self.api_key,
                url=self.url
            )
            
            # Initialize API client
            self.client = APIClient(credentials)
            
            # Initialize model
            self.model = ModelInference(
                model_id=self.model_id,
                api_client=self.client,
                project_id=self.project_id,
                params={
                    "max_new_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "top_k": self.top_k
                }
            )
            
            logger.info(f"IBM Bob client initialized with model: {self.model_id}")
        except Exception as e:
            logger.error(f"Failed to initialize IBM Bob client: {str(e)}")
            self.enabled = False
            self.client = None
            self.model = None
    
    def analyze_incident(self, bob_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze security incident using IBM Bob
        
        Args:
            bob_input: Bob input JSON with incident, attack_path, confidence, etc.
            
        Returns:
            Bob output JSON with analysis, fixes, tests, report, etc.
        """
        if self.mock_mode:
            return self._generate_mock_response(bob_input)
        
        if not self.enabled:
            logger.warning("Bob client not enabled, returning minimal response")
            return self._generate_fallback_response(bob_input)
        
        try:
            # Build prompt from bob_input
            from .bob_prompt_builder import BobPromptBuilder
            prompt_builder = BobPromptBuilder()
            prompt = prompt_builder.build_prompt(bob_input)
            
            # Call watsonx.ai
            logger.info("Sending request to IBM Bob...")
            response = self.model.generate_text(prompt=prompt)
            
            # Parse response
            from .bob_response_parser import BobResponseParser
            parser = BobResponseParser()
            bob_output = parser.parse_response(response, bob_input)
            
            logger.info("Successfully received and parsed Bob response")
            return bob_output
        except Exception as e:
            logger.error(f"Failed to analyze incident with Bob: {str(e)}")
            return self._generate_fallback_response(bob_input)
    
    def _generate_mock_response(self, bob_input: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock response for testing"""
        incident = bob_input.get('incident', {})
        attack_path = bob_input.get('attack_path', {})
        confidence = bob_input.get('confidence', {})
        
        incident_title = incident.get('title', 'Security Incident')
        severity = incident.get('severity', 'high')
        affected_files = incident.get('affected_files', [])
        affected_endpoints = incident.get('affected_endpoints', [])
        affected_tables = incident.get('affected_database_tables', [])
        
        # Generate mock response based on incident data
        mock_response = {
            "attack_type": "Credential leakage and abandoned API abuse",
            "target": f"Endpoints: {', '.join(affected_endpoints[:2]) if affected_endpoints else 'Unknown'}, Tables: {', '.join(affected_tables[:2]) if affected_tables else 'Unknown'}",
            "severity": severity,
            "confidence_assessment": f"Confidence score of {confidence.get('score', 0.85):.2f} based on correlated signals: {', '.join(confidence.get('reasons', [])[:3])}",
            "recommended_fixes": [
                {
                    "type": "immediate_action",
                    "description": "Rotate any exposed credentials immediately and revoke access to compromised keys."
                },
                {
                    "type": "code_fix",
                    "description": f"Move hardcoded credentials in {affected_files[0] if affected_files else 'affected files'} to environment variables or secret manager.",
                    "file": affected_files[0] if affected_files else None
                },
                {
                    "type": "api_fix",
                    "description": f"Disable or add authentication to {affected_endpoints[0] if affected_endpoints else 'deprecated endpoints'}.",
                    "endpoint": affected_endpoints[0] if affected_endpoints else None
                }
            ],
            "generated_security_tests": [
                {
                    "file": "tests/test_api_security.py",
                    "name": "test_deprecated_endpoint_disabled",
                    "purpose": "Ensure deprecated endpoints return 410 Gone or require authentication",
                    "code": f"def test_deprecated_endpoint_disabled(client):\n    \"\"\"Test that deprecated endpoint is properly secured\"\"\"\n    response = client.get('{affected_endpoints[0] if affected_endpoints else '/api/v1/export'}')\n    assert response.status_code in [401, 403, 410], 'Deprecated endpoint should be secured or disabled'"
                },
                {
                    "file": "tests/test_secrets.py",
                    "name": "test_no_hardcoded_secrets",
                    "purpose": "Verify no hardcoded secrets in codebase",
                    "code": "def test_no_hardcoded_secrets():\n    \"\"\"Scan for hardcoded secrets\"\"\"\n    import re\n    secret_patterns = [r'api[_-]?key\\s*=\\s*[\"\\'][^\"\\']', r'password\\s*=\\s*[\"\\'][^\"\\']']\n    # Add scanning logic\n    assert True, 'No hardcoded secrets found'"
                },
                {
                    "file": "tests/test_database_access.py",
                    "name": "test_sensitive_table_access_control",
                    "purpose": "Ensure sensitive database tables have proper access controls",
                    "code": f"def test_sensitive_table_access_control():\n    \"\"\"Test access controls on sensitive tables\"\"\"\n    # Test that {affected_tables[0] if affected_tables else 'users'} table requires authentication\n    assert True, 'Access controls verified'"
                }
            ],
            "incident_report": self._generate_mock_report(incident, attack_path, confidence),
            "ai_memory": {
                "memory_type": "security_prevention_rule",
                "incident_pattern": f"hardcoded_secret_in_abandoned_api_{incident.get('incident_id', 'unknown')}",
                "root_cause": "A legacy API contained static credentials and remained accessible without proper authentication.",
                "signals_to_watch": [
                    "Hardcoded credentials in legacy code",
                    "Deprecated endpoints still reachable",
                    "Unusual traffic patterns to old APIs",
                    "Database read spikes on sensitive tables"
                ],
                "prevention_rule": "Flag abandoned export/download APIs that contain static credentials or access sensitive data. Implement API versioning with sunset policies.",
                "recommended_tests": [
                    "Deprecated endpoints return 410 Gone",
                    "Export endpoints require admin role",
                    "Secrets loaded from environment variables",
                    "Rate limiting on data export endpoints"
                ],
                "severity_escalation_conditions": [
                    "Secret appears in application logs",
                    "Endpoint receives traffic from suspicious IPs",
                    "Database read spike exceeds baseline by 10x",
                    "Multiple related incidents within 24 hours"
                ]
            },
            "pr_draft": {
                "branch_name": f"security/fix-{incident.get('incident_id', 'incident').lower()}",
                "pr_title": f"Security: Fix {incident_title}",
                "pr_description": self._generate_pr_description(incident, affected_files, affected_endpoints),
                "files_to_change": affected_files[:5] if affected_files else ["config/secrets.env.example", "tests/test_security.py"]
            }
        }
        
        logger.info("Generated mock Bob response")
        return mock_response
    
    def _generate_mock_report(self, incident: Dict[str, Any], attack_path: Dict[str, Any], confidence: Dict[str, Any]) -> str:
        """Generate mock incident report"""
        incident_id = incident.get('incident_id', 'INC-UNKNOWN')
        title = incident.get('title', 'Security Incident')
        severity = incident.get('severity', 'high')
        
        report = f"""## Incident Report: {incident_id}

### {title}

**Severity:** {severity.upper()}  
**Confidence Score:** {confidence.get('score', 0.85):.2f}

#### Executive Summary
This incident involves a potential security breach through {title.lower()}. The system detected multiple correlated signals indicating a coordinated attack pattern.

#### Attack Path Analysis
The attack follows this progression:
"""
        
        nodes = attack_path.get('nodes', [])
        for i, node in enumerate(nodes, 1):
            report += f"{i}. **{node.get('label', 'Unknown')}** ({node.get('type', 'unknown')})\n"
        
        report += """
#### Confidence Assessment
"""
        for reason in confidence.get('reasons', []):
            report += f"- ✓ {reason}\n"
        
        if confidence.get('limitations'):
            report += "\n**Limitations:**\n"
            for limitation in confidence.get('limitations', []):
                report += f"- ⚠ {limitation}\n"
        
        report += """
#### Recommended Actions
1. **Immediate:** Rotate exposed credentials and disable vulnerable endpoints
2. **Short-term:** Implement security fixes and add regression tests
3. **Long-term:** Review similar patterns across codebase and strengthen security policies

#### Impact Assessment
- **Affected Systems:** """ + ', '.join(incident.get('affected_repos', ['Unknown'])) + """
- **Data at Risk:** Potentially sensitive user data and system credentials
- **Business Impact:** High - potential data breach and compliance violations

---
*Generated by IBM Bob Sentinel*
"""
        return report
    
    def _generate_pr_description(self, incident: Dict[str, Any], files: list, endpoints: list) -> str:
        """Generate PR description"""
        description = f"""## Security Fix: {incident.get('title', 'Security Issue')}

### Issue
This PR addresses security incident {incident.get('incident_id', 'INC-UNKNOWN')}.

### Changes
"""
        if files:
            description += "- Remove hardcoded credentials from:\n"
            for file in files[:3]:
                description += f"  - `{file}`\n"
        
        if endpoints:
            description += "- Secure or disable deprecated endpoints:\n"
            for endpoint in endpoints[:3]:
                description += f"  - `{endpoint}`\n"
        
        description += """
- Add environment variable configuration
- Implement security regression tests
- Update documentation

### Testing
- [x] Security tests pass
- [x] No hardcoded secrets detected
- [x] Deprecated endpoints properly secured

### Security Checklist
- [x] Credentials rotated
- [x] Secrets moved to environment variables
- [x] Access controls verified
- [x] Regression tests added

---
*Generated by IBM Bob Sentinel*
"""
        return description
    
    def _generate_fallback_response(self, bob_input: Dict[str, Any]) -> Dict[str, Any]:
        """Generate minimal fallback response when Bob is unavailable"""
        incident = bob_input.get('incident', {})
        
        return {
            "attack_type": "Security incident detected",
            "target": "System resources",
            "severity": incident.get('severity', 'medium'),
            "confidence_assessment": "Bob analysis unavailable - using basic classification",
            "recommended_fixes": [
                {
                    "type": "manual_review",
                    "description": "Manual security review required - Bob AI unavailable"
                }
            ],
            "generated_security_tests": [],
            "incident_report": f"# Incident Report\n\n{incident.get('title', 'Security Incident')}\n\nBob AI analysis unavailable. Manual review required.",
            "ai_memory": {},
            "pr_draft": {
                "branch_name": "security/manual-review",
                "pr_title": "Security: Manual review required",
                "pr_description": "Bob AI unavailable - manual security review needed"
            }
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check Bob client health status"""
        return {
            'enabled': self.enabled,
            'mock_mode': self.mock_mode,
            'watsonx_available': WATSONX_AVAILABLE,
            'model_id': self.model_id,
            'configured': bool(self.api_key and self.project_id)
        }


# Made with Bob