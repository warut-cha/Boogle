"""
Severity Classifier
Classifies security incidents using a 5-level severity scale with confidence scoring
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class SeverityClassifier:
    """Classifies incident severity on a 5-level scale"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize severity classifier
        
        Args:
            config: Severity configuration with weights and thresholds
        """
        self.config = config
        self.weights = config.get('weights', {
            'base_vulnerability': 0.4,
            'active_exploitation': 0.3,
            'sensitive_data': 0.2,
            'public_exposure': 0.1
        })
        self.thresholds = config.get('thresholds', {
            'critical': 0.85,
            'high': 0.70,
            'medium': 0.50,
            'low': 0.30
        })
    
    def classify(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify incident severity
        
        Args:
            incident: Incident dictionary with findings
            
        Returns:
            Severity classification with level and confidence
        """
        # Calculate severity score
        score = self._calculate_severity_score(incident)
        
        # Determine severity level
        level = self._score_to_level(score)
        
        # Calculate confidence
        confidence = self._calculate_confidence(incident)
        
        severity = {
            'level': level,
            'level_name': self._level_to_name(level),
            'score': score,
            'confidence': confidence,
            'factors': self._get_severity_factors(incident)
        }
        
        logger.info(f"Classified incident as Level {level} ({severity['level_name']}) with confidence {confidence:.2f}")
        
        return severity
    
    def _calculate_severity_score(self, incident: Dict[str, Any]) -> float:
        """Calculate weighted severity score"""
        # Base vulnerability score
        base_score = self._calculate_base_vulnerability_score(incident)
        
        # Active exploitation score
        exploitation_score = self._calculate_exploitation_score(incident)
        
        # Sensitive data score
        sensitive_data_score = self._calculate_sensitive_data_score(incident)
        
        # Public exposure score
        exposure_score = self._calculate_exposure_score(incident)
        
        # Weighted total
        total_score = (
            base_score * self.weights['base_vulnerability'] +
            exploitation_score * self.weights['active_exploitation'] +
            sensitive_data_score * self.weights['sensitive_data'] +
            exposure_score * self.weights['public_exposure']
        )
        
        return min(1.0, max(0.0, total_score))
    
    def _calculate_base_vulnerability_score(self, incident: Dict[str, Any]) -> float:
        """Calculate base vulnerability severity"""
        findings = incident.get('findings', [])
        
        if not findings:
            return 0.0
        
        # Critical vulnerability types
        critical_types = {
            'secret_leak': 0.9,
            'sql_injection_attempt': 0.95,
            'command_injection': 1.0,
            'privilege_escalation': 0.95,
            'brute_force_attack': 0.85
        }
        
        # High severity types
        high_types = {
            'deprecated_api': 0.7,
            'missing_authentication': 0.75,
            'large_data_export': 0.8,
            'sensitive_data_in_logs': 0.75,
            'cors_misconfiguration': 0.65
        }
        
        # Medium severity types
        medium_types = {
            'high_entropy_string': 0.5,
            'vulnerability': 0.6,
            'deprecated_endpoint': 0.5,
            'sensitive_endpoint': 0.55
        }
        
        # Calculate max severity from findings
        max_score = 0.0
        
        for finding in findings:
            finding_type = finding.get('type', '')
            
            if finding_type in critical_types:
                max_score = max(max_score, critical_types[finding_type])
            elif finding_type in high_types:
                max_score = max(max_score, high_types[finding_type])
            elif finding_type in medium_types:
                max_score = max(max_score, medium_types[finding_type])
            else:
                max_score = max(max_score, 0.3)
        
        return max_score
    
    def _calculate_exploitation_score(self, incident: Dict[str, Any]) -> float:
        """Calculate active exploitation indicators"""
        findings = incident.get('findings', [])
        
        # Indicators of active exploitation
        exploitation_indicators = [
            'sql_injection_attempt',
            'command_injection',
            'brute_force_attack',
            'path_traversal',
            'rapid_requests',
            'large_data_export',
            'privilege_escalation'
        ]
        
        # Check for exploitation indicators
        has_exploitation = any(
            f.get('type') in exploitation_indicators
            for f in findings
        )
        
        if has_exploitation:
            # Check for multiple indicators (coordinated attack)
            exploitation_count = sum(
                1 for f in findings
                if f.get('type') in exploitation_indicators
            )
            
            if exploitation_count >= 3:
                return 1.0  # Multiple exploitation indicators
            elif exploitation_count == 2:
                return 0.8
            else:
                return 0.6
        
        # Check correlation type
        correlation_type = incident.get('correlation_type', 'none')
        if correlation_type == 'attack_chain':
            return 0.9  # Attack chains indicate active exploitation
        elif correlation_type == 'temporal':
            return 0.7  # Temporal correlation suggests coordinated attack
        
        return 0.0
    
    def _calculate_sensitive_data_score(self, incident: Dict[str, Any]) -> float:
        """Calculate sensitive data involvement"""
        findings = incident.get('findings', [])
        
        # Sensitive data indicators
        sensitive_keywords = [
            'password', 'credential', 'secret', 'key', 'token',
            'payment', 'card', 'ssn', 'credit', 'cvv',
            'private', 'confidential', 'admin'
        ]
        
        # Check findings for sensitive data
        sensitive_count = 0
        
        for finding in findings:
            # Check finding type
            if finding.get('type') in ['secret_leak', 'sensitive_data_in_logs']:
                sensitive_count += 1
                continue
            
            # Check description and evidence
            text_to_check = (
                finding.get('description', '').lower() +
                ' ' +
                str(finding.get('evidence', {})).lower()
            )
            
            if any(keyword in text_to_check for keyword in sensitive_keywords):
                sensitive_count += 1
        
        if sensitive_count >= 3:
            return 1.0
        elif sensitive_count == 2:
            return 0.7
        elif sensitive_count == 1:
            return 0.5
        
        return 0.0
    
    def _calculate_exposure_score(self, incident: Dict[str, Any]) -> float:
        """Calculate public exposure risk"""
        findings = incident.get('findings', [])
        
        # Public exposure indicators
        exposure_indicators = {
            'missing_authentication': 0.9,
            'cors_misconfiguration': 0.8,
            'debug_enabled': 0.7,
            'deprecated_api_access': 0.6
        }
        
        max_exposure = 0.0
        
        for finding in findings:
            finding_type = finding.get('type', '')
            if finding_type in exposure_indicators:
                max_exposure = max(max_exposure, exposure_indicators[finding_type])
            
            # Check for public endpoints
            evidence = finding.get('evidence', {})
            if 'endpoint' in evidence or 'api' in str(evidence).lower():
                max_exposure = max(max_exposure, 0.5)
        
        return max_exposure
    
    def _score_to_level(self, score: float) -> int:
        """Convert score to severity level (1-5)"""
        if score >= self.thresholds['critical']:
            return 5  # Critical
        elif score >= self.thresholds['high']:
            return 4  # High
        elif score >= self.thresholds['medium']:
            return 3  # Medium
        elif score >= self.thresholds['low']:
            return 2  # Low
        else:
            return 1  # Informational
    
    def _level_to_name(self, level: int) -> str:
        """Convert level to name"""
        names = {
            5: 'critical',
            4: 'high',
            3: 'medium',
            2: 'low',
            1: 'info'
        }
        return names.get(level, 'unknown')
    
    def _calculate_confidence(self, incident: Dict[str, Any]) -> float:
        """Calculate confidence in severity classification"""
        findings = incident.get('findings', [])
        
        if not findings:
            return 0.5
        
        # Average confidence from findings
        confidences = [f.get('confidence', 0.7) for f in findings]
        avg_confidence = sum(confidences) / len(confidences)
        
        # Adjust based on correlation
        correlation_type = incident.get('correlation_type', 'none')
        
        if correlation_type == 'attack_chain':
            # High confidence for attack chains
            avg_confidence = min(1.0, avg_confidence + 0.1)
        elif correlation_type == 'temporal':
            # Moderate confidence boost for temporal correlation
            avg_confidence = min(1.0, avg_confidence + 0.05)
        elif correlation_type == 'none':
            # Slight confidence reduction for single findings
            avg_confidence = max(0.5, avg_confidence - 0.05)
        
        # Adjust based on finding count
        if len(findings) >= 5:
            avg_confidence = min(1.0, avg_confidence + 0.1)
        elif len(findings) >= 3:
            avg_confidence = min(1.0, avg_confidence + 0.05)
        
        return round(avg_confidence, 2)
    
    def _get_severity_factors(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Get factors contributing to severity"""
        findings = incident.get('findings', [])
        
        return {
            'finding_count': len(findings),
            'finding_types': list(set(f.get('type') for f in findings)),
            'correlation_type': incident.get('correlation_type', 'none'),
            'has_exploitation_indicators': any(
                f.get('type') in [
                    'sql_injection_attempt', 'command_injection',
                    'brute_force_attack', 'privilege_escalation'
                ]
                for f in findings
            ),
            'has_sensitive_data': any(
                f.get('type') in ['secret_leak', 'sensitive_data_in_logs']
                for f in findings
            ),
            'has_public_exposure': any(
                f.get('type') in ['missing_authentication', 'cors_misconfiguration']
                for f in findings
            )
        }
    
    def get_severity_description(self, level: int) -> str:
        """Get detailed description for severity level"""
        descriptions = {
            5: "Critical: Active exploitation or data breach in progress. Immediate action required.",
            4: "High: Leaked credentials or exposed sensitive APIs. Urgent remediation needed.",
            3: "Medium: Vulnerable code without active exploitation. Should be addressed soon.",
            2: "Low: Potential risk with no sensitive data involved. Address in regular maintenance.",
            1: "Informational: Technical debt or unused code with no security implications."
        }
        return descriptions.get(level, "Unknown severity level")

# Made with Bob
