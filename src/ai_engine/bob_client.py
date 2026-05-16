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
        """Generate contextually appropriate mock response based on incident data"""
        # Extract incident data
        incident = bob_input.get('incident', {})
        attack_path = bob_input.get('attack_path', {})
        confidence = bob_input.get('confidence', {})
        
        incident_id = incident.get('incident_id', 'INC-000')
        severity = incident.get('severity', 'high')
        severity_level = incident.get('severity_level', 3)
        findings = incident.get('findings', [])
        affected_files = incident.get('affected_files', [])
        affected_endpoints = incident.get('affected_endpoints', [])
        affected_tables = incident.get('affected_database_tables', [])
        affected_repos = incident.get('affected_repos', [])
        
        # Extract unique finding types
        unique_finding_types = list({f.get('finding_type') for f in findings if f.get('finding_type')})
        primary_finding_type = unique_finding_types[0] if unique_finding_types else 'unknown'
        
        # Get primary assets from first relevant finding
        primary_file = next((f.get('file') for f in findings if f.get('file')), None)
        primary_endpoint = next((f.get('endpoint') for f in findings if f.get('endpoint')), None)
        primary_table = next((f.get('database_table') for f in findings if f.get('database_table')), None)
        primary_line = next((f.get('line') for f in findings if f.get('line')), None)
        repo_name = affected_repos[0].replace('-', '_') if affected_repos else 'unknown'
        
        # Determine attack type based on finding types
        attack_type = self._determine_attack_type(unique_finding_types)
        
        # Build target description
        target = self._build_target_description(affected_endpoints, affected_tables, affected_files)
        
        # Build confidence assessment
        confidence_assessment = self._build_confidence_assessment(confidence)
        
        # Generate fixes based on finding types
        recommended_fixes = self._generate_fixes(findings, unique_finding_types, severity)
        
        # Generate security tests
        generated_security_tests = self._generate_tests(unique_finding_types, incident_id, findings)
        
        # Generate incident report
        incident_report = self._generate_contextual_report(
            incident, attack_path, confidence, findings, unique_finding_types
        )
        
        # Generate AI memory
        ai_memory = self._generate_ai_memory(
            primary_finding_type, repo_name, findings, primary_endpoint,
            primary_file, primary_table, generated_security_tests
        )
        
        # Generate PR draft
        pr_draft = self._generate_contextual_pr_draft(
            incident_id, severity, attack_type, recommended_fixes,
            generated_security_tests, unique_finding_types, findings
        )
        
        mock_response = {
            "attack_type": attack_type,
            "target": target,
            "severity": severity,
            "confidence_assessment": confidence_assessment,
            "recommended_fixes": recommended_fixes,
            "generated_security_tests": generated_security_tests,
            "incident_report": incident_report,
            "ai_memory": ai_memory,
            "pr_draft": pr_draft
        }
        
        logger.info(f"Generated contextual mock Bob response for {incident_id}")
        return mock_response
    
    def _determine_attack_type(self, finding_types: list) -> str:
        """Determine attack type based on finding types present"""
        finding_set = frozenset(finding_types)
        
        # Attack type mapping
        attack_type_map = {
            frozenset(['hardcoded_secret', 'deprecated_api']): 'Credential leakage via abandoned API',
            frozenset(['hardcoded_secret', 'runtime_anomaly']): 'Exposed credential with active exploitation',
            frozenset(['database_url', 'database_anomaly']): 'Database credential exposure and anomalous access',
            frozenset(['runtime_anomaly', 'database_anomaly']): 'Runtime exploitation leading to data exfiltration',
            frozenset(['deprecated_api', 'runtime_anomaly']): 'Legacy endpoint abuse',
            frozenset(['infrastructure_risk']): 'Infrastructure misconfiguration exposure',
        }
        
        # Find best match by checking if any key is a subset of finding_set
        for key, attack_type in attack_type_map.items():
            if key.issubset(finding_set):
                return attack_type
        
        # Fallback based on primary finding type
        if 'hardcoded_secret' in finding_types or 'database_url' in finding_types:
            return 'Credential exposure incident'
        elif 'runtime_anomaly' in finding_types:
            return 'Runtime security anomaly'
        elif 'database_anomaly' in finding_types:
            return 'Database access anomaly'
        elif 'deprecated_api' in finding_types:
            return 'Legacy API security issue'
        
        return 'Multi-vector security incident'
    
    def _build_target_description(self, endpoints: list, tables: list, files: list) -> str:
        """Build target description from affected assets"""
        parts = []
        
        if endpoints:
            parts.append(f"endpoint {endpoints[0]}")
        if tables:
            parts.append(f"{tables[0]} database table")
        if files and not endpoints:
            parts.append(f"in {files[0]}")
        
        return ' and '.join(parts) if parts else 'system resources'
    
    def _build_confidence_assessment(self, confidence: Dict[str, Any]) -> str:
        """Build confidence assessment from confidence data"""
        score = confidence.get('score', 0.75)
        reasons = confidence.get('reasons', [])
        limitations = confidence.get('limitations', [])
        
        assessment = f"{int(score * 100)}% confidence"
        
        if reasons:
            reason_text = ' and '.join(reasons[:2])
            assessment += f" because {reason_text}"
        
        if limitations:
            assessment += f". Limitations: {limitations[0]}"
        
        return assessment
    
    def _generate_fixes(self, findings: list, finding_types: list, severity: str) -> list:
        """Generate fixes based on finding types present"""
        fixes = []
        
        # Fix rules for each finding type
        fix_rules = {
            'hardcoded_secret': {
                'type': 'immediate_action',
                'template': 'Rotate the exposed credential found in {file}:{line} immediately.'
            },
            'deprecated_api': {
                'type': 'api_fix',
                'template': 'Disable or authenticate {endpoint}. Return 410 Gone for deprecated routes.'
            },
            'database_anomaly': {
                'type': 'config_fix',
                'template': 'Add read-rate alerting on {table} table. Alert when reads exceed 10x baseline.'
            },
            'runtime_anomaly': {
                'type': 'immediate_action',
                'template': 'Block or rate-limit traffic to {endpoint} pending investigation.'
            },
            'infrastructure_risk': {
                'type': 'config_fix',
                'template': 'Remove {endpoint} from gateway configuration or add IP allowlist.'
            },
            'database_url': {
                'type': 'code_fix',
                'template': 'Move database URL from {file} to environment variable DATABASE_URL.'
            },
        }
        
        # Generate one fix per finding type
        for finding_type in finding_types:
            if finding_type in fix_rules:
                rule = fix_rules[finding_type]
                # Find a relevant finding of this type
                relevant_finding = next((f for f in findings if f.get('finding_type') == finding_type), {})
                
                description = rule['template'].format(
                    file=relevant_finding.get('file', 'affected file'),
                    line=relevant_finding.get('line', ''),
                    endpoint=relevant_finding.get('endpoint', 'affected endpoint'),
                    table=relevant_finding.get('database_table', 'affected table')
                )
                
                fixes.append({
                    'type': rule['type'],
                    'description': description
                })
        
        # Always add a test fix at the end
        fixes.append({
            'type': 'test_fix',
            'description': f'Add security regression tests for all {severity} findings in this incident.'
        })
        
        return fixes if fixes else [{'type': 'manual_review', 'description': 'Manual security review required.'}]
    
    def _generate_tests(self, finding_types: list, incident_id: str, findings: list) -> list:
        """Generate security tests based on finding types"""
        tests = []
        
        # Test templates for each finding type
        test_templates = {
            'hardcoded_secret': {
                'name': 'test_no_hardcoded_secrets',
                'purpose': 'Verify no hardcoded secrets in {file}',
                'code': '''def test_no_hardcoded_secrets():
    """Scan for secret patterns in affected file"""
    import re
    secret_patterns = [r'api[_-]?key\\s*=\\s*["\'][^"\']+', r'password\\s*=\\s*["\'][^"\']+']
    with open('{file}') as f:
        content = f.read()
        for pattern in secret_patterns:
            assert not re.search(pattern, content), f"Hardcoded secret found in {file}"'''
            },
            'deprecated_api': {
                'name': 'test_deprecated_endpoint_disabled',
                'purpose': 'Ensure {endpoint} returns 404 or 410',
                'code': '''def test_deprecated_endpoint_disabled(client):
    """Test that deprecated endpoint is properly disabled"""
    response = client.get('{endpoint}')
    assert response.status_code in [404, 410], "Deprecated endpoint should return 404 or 410"'''
            },
            'database_anomaly': {
                'name': 'test_database_read_rate_alerting',
                'purpose': 'Verify read rate alerting on {table} table',
                'code': '''def test_database_read_rate_alerting():
    """Test that read rate alerting triggers above threshold"""
    # Simulate high read rate on {table}
    # Verify alert is triggered when reads exceed 10x baseline
    assert True, "Read rate alerting configured"'''
            },
            'runtime_anomaly': {
                'name': 'test_endpoint_rate_limiting',
                'purpose': 'Ensure rate limiting is active on {endpoint}',
                'code': '''def test_endpoint_rate_limiting(client):
    """Test that rate limiting is enforced"""
    for _ in range(100):
        response = client.get('{endpoint}')
    assert response.status_code == 429, "Rate limiting should be active"'''
            },
            'infrastructure_risk': {
                'name': 'test_endpoint_not_publicly_accessible',
                'purpose': 'Verify {endpoint} is not reachable from public network',
                'code': '''def test_endpoint_not_publicly_accessible():
    """Test that endpoint is not accessible from public network"""
    import requests
    try:
        response = requests.get('https://public-ip/{endpoint}', timeout=5)
        assert False, "Endpoint should not be publicly accessible"
    except requests.exceptions.RequestException:
        pass  # Expected - endpoint not accessible'''
            },
        }
        
        # Generate one test per unique finding type
        for finding_type in finding_types:
            if finding_type in test_templates:
                template = test_templates[finding_type]
                # Find a relevant finding of this type
                relevant_finding = next((f for f in findings if f.get('finding_type') == finding_type), {})
                
                test_file = f"tests/test_{finding_type}_{incident_id.lower()}.py"
                purpose = template['purpose'].format(
                    file=relevant_finding.get('file', 'affected file'),
                    endpoint=relevant_finding.get('endpoint', '/unknown'),
                    table=relevant_finding.get('database_table', 'unknown')
                )
                code = template['code'].format(
                    file=relevant_finding.get('file', 'affected_file.py'),
                    endpoint=relevant_finding.get('endpoint', '/unknown'),
                    table=relevant_finding.get('database_table', 'unknown')
                )
                
                tests.append({
                    'file': test_file,
                    'name': template['name'],
                    'purpose': purpose,
                    'code': code
                })
        
        return tests if tests else []
    
    def _generate_contextual_report(self, incident: Dict[str, Any], attack_path: Dict[str, Any],
                                   confidence: Dict[str, Any], findings: list, finding_types: list) -> str:
        """Generate contextual incident report"""
        incident_id = incident.get('incident_id', 'INC-UNKNOWN')
        severity = incident.get('severity', 'high')
        severity_level = incident.get('severity_level', 3)
        affected_repos = incident.get('affected_repos', [])
        confidence_score = confidence.get('score', 0.75)
        
        report = f"""## Security Incident Report

**Incident ID:** {incident_id}
**Severity:** {severity.upper()} (Level {severity_level})
**Confidence:** {int(confidence_score * 100)}%
**Affected Repos:** {', '.join(affected_repos) if affected_repos else 'Unknown'}

### Summary
{self._generate_summary(incident, finding_types)}

### Attack Chain
"""
        
        nodes = attack_path.get('nodes', [])
        for i, node in enumerate(nodes, 1):
            report += f"{i}. **{node.get('label', 'Unknown')}** ({node.get('type', 'unknown')})\n"
        
        report += f"\n### Evidence ({len(findings)} findings)\n"
        for finding in findings[:5]:  # Show first 5 findings
            finding_id = finding.get('finding_id', 'FIND-???')
            evidence = finding.get('evidence', 'No evidence')
            location = finding.get('file') or finding.get('endpoint') or 'unknown location'
            report += f"- **{finding_id}**: {evidence} in {location}\n"
        
        report += "\n### Confidence Factors\n**Supporting:**\n"
        for reason in confidence.get('reasons', []):
            report += f"- {reason}\n"
        
        if confidence.get('limitations'):
            report += "\n**Limitations:**\n"
            for limitation in confidence.get('limitations', []):
                report += f"- {limitation}\n"
        
        report += "\n### Recommended Actions\n"
        report += "#### Immediate (within 1 hour)\n"
        report += "- Rotate any exposed credentials\n"
        report += "- Block or rate-limit suspicious traffic\n"
        
        report += "\n#### Short-term (within 24 hours)\n"
        report += "- Implement code fixes for vulnerabilities\n"
        report += "- Add authentication to exposed endpoints\n"
        
        report += "\n#### Long-term\n"
        report += "- Add security regression tests\n"
        report += "- Review similar patterns across codebase\n"
        
        report += "\n---\n*Generated by IBM Bob Sentinel*\n"
        return report
    
    def _generate_summary(self, incident: Dict[str, Any], finding_types: list) -> str:
        """Generate incident summary based on finding types"""
        title = incident.get('title', 'Security incident')
        
        if 'hardcoded_secret' in finding_types:
            return f"{title}. Hardcoded credentials detected in source code, creating risk of unauthorized access."
        elif 'runtime_anomaly' in finding_types and 'database_anomaly' in finding_types:
            return f"{title}. Suspicious runtime activity correlated with database access anomalies, indicating possible data exfiltration."
        elif 'deprecated_api' in finding_types:
            return f"{title}. Legacy API endpoints remain accessible without proper security controls."
        else:
            return f"{title}. Multiple security signals detected requiring investigation."
    
    def _generate_ai_memory(self, primary_finding_type: str, repo_name: str, findings: list,
                           primary_endpoint: Optional[str], primary_file: Optional[str],
                           primary_table: Optional[str], generated_tests: list) -> Dict[str, Any]:
        """Generate AI memory based on incident patterns"""
        return {
            'memory_type': 'security_prevention_rule',
            'incident_pattern': f'{primary_finding_type}_in_{repo_name}',
            'root_cause': f'{primary_finding_type} in {primary_file or primary_endpoint or "system"} created security vulnerability.',
            'signals_to_watch': [f.get('evidence', 'Unknown signal') for f in findings[:3]],
            'prevention_rule': f'Monitor {primary_endpoint or primary_file or "system resources"} for {primary_finding_type} patterns.',
            'recommended_tests': [t['name'] for t in generated_tests],
            'severity_escalation_conditions': [
                f'More than 3 {primary_finding_type} findings in same repo',
                'Confidence score exceeds 0.9',
                f'{primary_table or primary_endpoint or "system"} shows anomalous activity',
            ]
        }
    
    def _generate_contextual_pr_draft(self, incident_id: str, severity: str, attack_type: str,
                                     recommended_fixes: list, generated_tests: list,
                                     finding_types: list, findings: list) -> Dict[str, Any]:
        """Generate contextual PR draft"""
        primary_finding_type = finding_types[0] if finding_types else 'security_issue'
        
        pr_description = f"""## {incident_id}

**Severity:** {severity.upper()}
**Attack type:** {attack_type}

### Changes
"""
        for fix in recommended_fixes:
            pr_description += f"- {fix['type']}: {fix['description']}\n"
        
        pr_description += "\n### Testing\n"
        for test in generated_tests:
            pr_description += f"- `{test['name']}`\n"
        
        # Collect files to change
        files_to_change = list(set(
            [f.get('file') for f in findings if f.get('file')]
            + [t['file'] for t in generated_tests]
        ))
        
        return {
            'branch_name': f'security/fix-{incident_id.lower()}-{primary_finding_type}',
            'pr_title': f'Security Fix ({severity.upper()}): {attack_type} — {incident_id}',
            'pr_description': pr_description,
            'files_to_change': files_to_change if files_to_change else ['config/security.yaml', 'tests/test_security.py']
        }
    
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