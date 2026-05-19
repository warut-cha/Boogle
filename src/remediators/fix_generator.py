"""
Fix Generator
Generates specific code fixes and remediation steps for security incidents
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class FixGenerator:
    """Generates remediation fixes for security incidents"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize fix generator"""
        self.config = config
        self.auto_generate_fixes = config.get('auto_generate_fixes', True)
        self.auto_generate_tests = config.get('auto_generate_tests', True)
    
    def generate(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate remediation for incident
        
        Args:
            incident: Incident dictionary
            
        Returns:
            Remediation dictionary with fixes and tests
        """
        findings = incident.get('findings', [])
        
        remediation = {
            'immediate_actions': self._generate_immediate_actions(incident),
            'code_fixes': self._generate_code_fixes(findings),
            'configuration_changes': self._generate_config_changes(findings),
            'security_tests': self._generate_security_tests(findings) if self.auto_generate_tests else [],
            'prevention_steps': self._generate_prevention_steps(incident)
        }
        
        return remediation
    
    def _generate_immediate_actions(self, incident: Dict[str, Any]) -> List[str]:
        """Generate immediate containment actions"""
        severity_level = incident.get('severity', {}).get('level', 3)
        actions = []
        
        if severity_level >= 5:
            actions.append("🚨 CRITICAL: Isolate affected systems immediately")
            actions.append("🔒 Rotate all exposed credentials within 1 hour")
            actions.append("🛡️ Enable enhanced monitoring and alerting")
            actions.append("📞 Notify security team and stakeholders")
        elif severity_level >= 4:
            actions.append("⚠️ HIGH: Review and rotate exposed credentials within 24 hours")
            actions.append("🔍 Investigate access logs for unauthorized activity")
            actions.append("🚫 Block suspicious IP addresses if identified")
        else:
            actions.append("📋 Review findings and plan remediation")
            actions.append("📅 Schedule fixes in next sprint")
        
        return actions
    
    def _generate_code_fixes(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate specific code fixes"""
        fixes = []
        
        for finding in findings:
            finding_type = finding.get('type')
            file_path = finding.get('file_path')
            line_number = finding.get('line_number')
            
            fix = {
                'file': file_path,
                'line': line_number,
                'finding_type': finding_type,
                'description': finding.get('remediation', 'Fix required'),
                'before': finding.get('line_content', ''),
                'after': self._generate_fix_code(finding)
            }
            
            fixes.append(fix)
        
        return fixes
    
    def _generate_fix_code(self, finding: Dict[str, Any]) -> str:
        """Generate specific fix code"""
        finding_type = finding.get('type')
        
        if finding_type == 'secret_leak':
            return "# Use environment variable: os.getenv('SECRET_KEY')"
        elif finding_type == 'sql_injection_attempt':
            return "# Use parameterized query: cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
        elif finding_type == 'missing_authentication':
            return "@login_required  # Add authentication decorator"
        elif finding_type == 'command_injection':
            return "# Use subprocess with list args: subprocess.run(['command', 'arg'], shell=False)"
        else:
            return "# Review and fix according to remediation guidance"
    
    def _generate_config_changes(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate configuration changes"""
        changes = []
        finding_types = [f.get('type') for f in findings]
        
        if 'secret_leak' in finding_types:
            changes.append("Add secrets to environment variables or secret management service")
            changes.append("Update .gitignore to exclude .env files")
        
        if 'cors_misconfiguration' in finding_types:
            changes.append("Restrict CORS to specific trusted domains")
            changes.append("Update CORS_ALLOW_ORIGINS in configuration")
        
        if 'debug_enabled' in finding_types:
            changes.append("Set DEBUG=False in production environment")
            changes.append("Remove debug endpoints from production builds")
        
        return changes
    
    def _generate_security_tests(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate security test specifications"""
        tests = []
        finding_types = set(f.get('type') for f in findings)
        
        if 'secret_leak' in finding_types:
            tests.append("test_no_hardcoded_secrets: Scan all files for secret patterns")
            tests.append("test_environment_variables: Verify secrets loaded from env")
        
        if 'sql_injection_attempt' in finding_types or 'vulnerability' in finding_types:
            tests.append("test_sql_injection_protection: Attempt SQL injection on all inputs")
            tests.append("test_parameterized_queries: Verify all queries use parameters")
        
        if 'missing_authentication' in finding_types:
            tests.append("test_authentication_required: Verify protected endpoints require auth")
            tests.append("test_unauthorized_access: Attempt access without credentials")
        
        if 'deprecated_api' in finding_types:
            tests.append("test_deprecated_endpoints_removed: Verify old APIs return 410")
            tests.append("test_api_version_enforcement: Check only current version accessible")
        
        return tests
    
    def _generate_prevention_steps(self, incident: Dict[str, Any]) -> List[str]:
        """Generate long-term prevention steps"""
        return [
            "Implement automated security scanning in CI/CD pipeline",
            "Add pre-commit hooks for secret detection",
            "Conduct regular security code reviews",
            "Update security training for development team",
            "Implement security testing in QA process",
            "Schedule quarterly security audits"
        ]

# Made with Bob
