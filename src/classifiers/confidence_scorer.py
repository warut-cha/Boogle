"""
Confidence Scorer
Calculates confidence scores for incident severity classifications
"""

from typing import Dict, Any, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ConfidenceScorer:
    """Calculates confidence scores for security incidents"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize confidence scorer
        
        Args:
            config: Configuration dictionary (optional)
        """
        self.config = config or {}
        self.min_confidence = self.config.get('min_confidence', 0.5)
        self.max_confidence = self.config.get('max_confidence', 0.99)
    
    def calculate_confidence(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate confidence score for an incident
        
        Args:
            incident: Incident dictionary with findings
            
        Returns:
            Dictionary with confidence_score, confidence_reasons, and confidence_limitations
        """
        findings = incident.get('findings', [])
        
        if not findings:
            return {
                'confidence_score': 0.5,
                'confidence_reasons': ['No findings available'],
                'confidence_limitations': ['Insufficient data for analysis']
            }
        
        # Calculate base confidence from multiple factors
        base_score = self._calculate_base_confidence(findings)
        
        # Calculate correlation confidence boost
        correlation_boost = self._calculate_correlation_boost(incident)
        
        # Calculate evidence quality score
        evidence_score = self._calculate_evidence_quality(findings)
        
        # Calculate finding diversity score
        diversity_score = self._calculate_finding_diversity(findings)
        
        # Combine scores with weights
        confidence_score = (
            base_score * 0.4 +
            correlation_boost * 0.3 +
            evidence_score * 0.2 +
            diversity_score * 0.1
        )
        
        # Clamp to valid range
        confidence_score = max(self.min_confidence, min(self.max_confidence, confidence_score))
        
        # Round to 2 decimal places
        confidence_score = round(confidence_score, 2)
        
        # Generate reasons and limitations
        reasons = self._generate_confidence_reasons(incident, findings)
        limitations = self._generate_confidence_limitations(incident, findings)
        
        logger.info(f"Calculated confidence score: {confidence_score} for incident {incident.get('incident_id', 'unknown')}")
        
        return {
            'confidence_score': confidence_score,
            'confidence_reasons': reasons,
            'confidence_limitations': limitations
        }
    
    def _calculate_base_confidence(self, findings: List[Dict[str, Any]]) -> float:
        """Calculate base confidence from finding quality"""
        if not findings:
            return 0.5
        
        # Start with average of individual finding confidences
        total_confidence = 0.0
        count = 0
        
        for finding in findings:
            # Use severity_hint as a proxy for confidence if not explicitly provided
            severity = finding.get('severity_hint', 'medium').lower()
            
            # Map severity to confidence
            severity_confidence = {
                'critical': 0.9,
                'high': 0.85,
                'medium': 0.75,
                'low': 0.65,
                'info': 0.6
            }
            
            finding_confidence = severity_confidence.get(severity, 0.7)
            
            # Boost confidence if we have specific evidence
            if finding.get('evidence'):
                finding_confidence = min(0.95, finding_confidence + 0.05)
            
            # Boost confidence if we have file location
            if finding.get('file') and finding.get('line'):
                finding_confidence = min(0.95, finding_confidence + 0.05)
            
            total_confidence += finding_confidence
            count += 1
        
        return total_confidence / count if count > 0 else 0.7
    
    def _calculate_correlation_boost(self, incident: Dict[str, Any]) -> float:
        """Calculate confidence boost from correlation"""
        correlation_type = incident.get('correlation_type', 'none')
        finding_count = len(incident.get('findings', []))
        
        # Base correlation confidence
        correlation_scores = {
            'attack_chain': 0.95,
            'temporal': 0.85,
            'credential': 0.90,
            'target': 0.80,
            'none': 0.70
        }
        
        base_score = correlation_scores.get(correlation_type, 0.70)
        
        # Boost for multiple findings
        if finding_count >= 5:
            base_score = min(0.98, base_score + 0.10)
        elif finding_count >= 3:
            base_score = min(0.95, base_score + 0.05)
        
        return base_score
    
    def _calculate_evidence_quality(self, findings: List[Dict[str, Any]]) -> float:
        """Calculate confidence based on evidence quality"""
        if not findings:
            return 0.5
        
        quality_score = 0.0
        
        for finding in findings:
            finding_quality = 0.5  # Base quality
            
            # Check for specific evidence
            if finding.get('evidence'):
                evidence = finding['evidence']
                if len(str(evidence)) > 20:  # Substantial evidence
                    finding_quality += 0.2
                else:
                    finding_quality += 0.1
            
            # Check for masked values (indicates actual secret found)
            if finding.get('masked_value'):
                finding_quality += 0.15
            
            # Check for specific location
            if finding.get('file'):
                finding_quality += 0.1
            
            # Check for endpoint or database table
            if finding.get('endpoint') or finding.get('database_table'):
                finding_quality += 0.1
            
            quality_score += min(1.0, finding_quality)
        
        return quality_score / len(findings)
    
    def _calculate_finding_diversity(self, findings: List[Dict[str, Any]]) -> float:
        """Calculate confidence based on finding diversity"""
        if not findings:
            return 0.5
        
        # Count unique categories
        categories = set(f.get('category', 'unknown') for f in findings)
        sources = set(f.get('source', 'unknown') for f in findings)
        finding_types = set(f.get('finding_type', 'unknown') for f in findings)
        
        # More diverse findings = higher confidence in correlation
        diversity_score = 0.5
        
        if len(categories) >= 3:
            diversity_score += 0.2
        elif len(categories) >= 2:
            diversity_score += 0.1
        
        if len(sources) >= 2:
            diversity_score += 0.15
        
        if len(finding_types) >= 3:
            diversity_score += 0.15
        
        return min(1.0, diversity_score)
    
    def _generate_confidence_reasons(self, incident: Dict[str, Any], 
                                     findings: List[Dict[str, Any]]) -> List[str]:
        """Generate human-readable confidence reasons"""
        reasons = []
        
        # Check for hardcoded secrets
        if any(f.get('finding_type') == 'hardcoded_secret' for f in findings):
            reasons.append("Hardcoded API key found")
        
        # Check for deprecated APIs
        if any(f.get('finding_type') == 'deprecated_api' for f in findings):
            if any(f.get('endpoint') for f in findings):
                endpoint = next((f.get('endpoint') for f in findings if f.get('endpoint')), None)
                reasons.append(f"Deprecated export endpoint is still reachable")
        
        # Check for runtime anomalies
        if any(f.get('finding_type') == 'runtime_anomaly' for f in findings):
            reasons.append("Suspicious repeated access detected")
        
        # Check for database anomalies
        if any(f.get('finding_type') == 'database_anomaly' for f in findings):
            db_finding = next((f for f in findings if f.get('finding_type') == 'database_anomaly'), None)
            if db_finding and db_finding.get('database_table'):
                reasons.append(f"{db_finding['database_table'].capitalize()} table showed abnormal read activity")
        
        # Check for infrastructure risks
        if any(f.get('finding_type') == 'infrastructure_risk' for f in findings):
            reasons.append("Infrastructure configuration exposes vulnerable endpoint")
        
        # Check correlation type
        correlation_type = incident.get('correlation_type', 'none')
        if correlation_type == 'attack_chain':
            reasons.append("Multiple attack stages detected in sequence")
        elif correlation_type == 'temporal':
            reasons.append("Multiple findings occurred within short time window")
        
        # Check for multiple repos affected
        repos = set(f.get('repo_name') for f in findings if f.get('repo_name'))
        if len(repos) > 1:
            reasons.append(f"Multiple repositories affected ({len(repos)} repos)")
        
        # If no specific reasons, add generic one
        if not reasons:
            reasons.append(f"Based on {len(findings)} correlated findings")
        
        return reasons
    
    def _generate_confidence_limitations(self, incident: Dict[str, Any], 
                                         findings: List[Dict[str, Any]]) -> List[str]:
        """Generate human-readable confidence limitations"""
        limitations = []
        
        # Check for missing external confirmation
        has_external_evidence = any(
            f.get('source') not in ['rust_scanner', 'python_analyzer'] 
            for f in findings
        )
        
        if not has_external_evidence:
            limitations.append("No confirmed external exfiltration destination found")
        
        # Check for missing runtime evidence
        has_runtime = any(f.get('finding_type') == 'runtime_anomaly' for f in findings)
        if not has_runtime:
            limitations.append("No runtime behavior evidence available")
        
        # Check for single source
        sources = set(f.get('source', 'unknown') for f in findings)
        if len(sources) == 1:
            limitations.append(f"All findings from single source ({list(sources)[0]})")
        
        # Check for missing database evidence
        has_db = any(f.get('database_table') for f in findings)
        if not has_db and incident.get('correlation_type') != 'none':
            limitations.append("No database activity evidence available")
        
        # Check for low finding count
        if len(findings) < 3:
            limitations.append("Limited number of correlated findings")
        
        # Check for missing file locations
        files_with_location = sum(1 for f in findings if f.get('file') and f.get('line'))
        if files_with_location < len(findings) / 2:
            limitations.append("Some findings lack specific file locations")
        
        # If no limitations found, add a generic one
        if not limitations:
            limitations.append("Analysis based on available data only")
        
        return limitations


# Made with Bob