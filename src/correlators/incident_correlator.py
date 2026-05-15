"""
Incident Correlator
Groups related security findings into unified incidents using multi-dimensional correlation
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Set
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class IncidentCorrelator:
    """Correlates security findings into unified incidents"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize incident correlator
        
        Args:
            config: Correlation configuration
        """
        self.config = config
        self.time_window_minutes = config.get('time_window_minutes', 120)
        self.min_confidence = config.get('min_confidence', 0.7)
        self.correlation_types = config.get('correlation_types', [
            'temporal', 'credential', 'target', 'actor', 'attack_chain'
        ])
    
    def correlate(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Correlate findings into incidents
        
        Args:
            findings: List of security findings
            
        Returns:
            List of correlated incidents
        """
        if not findings:
            return []
        
        logger.info(f"Correlating {len(findings)} findings into incidents")
        
        # Add timestamps to findings if missing
        for i, finding in enumerate(findings):
            if 'timestamp' not in finding:
                finding['timestamp'] = datetime.now().isoformat()
        
        # Group findings by correlation dimensions
        incidents = []
        processed_findings = set()
        
        # First pass: Identify attack chains (sequential attacks)
        attack_chain_incidents = self._correlate_attack_chains(findings, processed_findings)
        incidents.extend(attack_chain_incidents)
        
        # Second pass: Correlate by IP address and time
        temporal_incidents = self._correlate_temporal(findings, processed_findings)
        incidents.extend(temporal_incidents)
        
        # Third pass: Correlate by credentials/secrets
        credential_incidents = self._correlate_credentials(findings, processed_findings)
        incidents.extend(credential_incidents)
        
        # Fourth pass: Correlate by target (file, endpoint, table)
        target_incidents = self._correlate_targets(findings, processed_findings)
        incidents.extend(target_incidents)
        
        # Fifth pass: Create incidents for remaining findings
        remaining_findings = [f for i, f in enumerate(findings) if i not in processed_findings]
        for finding in remaining_findings:
            incident = self._create_single_finding_incident(finding)
            incidents.append(incident)
        
        # Assign incident IDs and timestamps
        for i, incident in enumerate(incidents, start=1):
            incident['id'] = f"INC-{datetime.now().year}-{i:03d}"
            if 'timestamp' not in incident:
                incident['timestamp'] = datetime.now().isoformat()
        
        logger.info(f"Created {len(incidents)} incidents from {len(findings)} findings")
        
        return incidents
    
    def _correlate_attack_chains(self, findings: List[Dict[str, Any]], 
                                 processed: Set[int]) -> List[Dict[str, Any]]:
        """Correlate findings that form attack chains"""
        incidents = []
        
        # Define attack chain patterns
        attack_patterns = [
            {
                'name': 'Credential Theft to Data Exfiltration',
                'stages': ['secret_leak', 'large_data_export', 'deprecated_api_access'],
                'severity': 'critical'
            },
            {
                'name': 'SQL Injection to Database Breach',
                'stages': ['sql_injection_attempt', 'vulnerability', 'large_data_export'],
                'severity': 'critical'
            },
            {
                'name': 'Deprecated API Exploitation',
                'stages': ['deprecated_api', 'missing_authentication', 'privilege_escalation'],
                'severity': 'high'
            }
        ]
        
        for pattern in attack_patterns:
            # Find findings matching this pattern
            matching_findings = []
            
            for stage in pattern['stages']:
                stage_findings = [
                    (i, f) for i, f in enumerate(findings)
                    if f.get('type') == stage and i not in processed
                ]
                
                if stage_findings:
                    matching_findings.append(stage_findings[0])
            
            # If we found multiple stages, create an incident
            if len(matching_findings) >= 2:
                finding_indices = [idx for idx, _ in matching_findings]
                finding_objects = [f for _, f in matching_findings]
                
                incident = {
                    'title': pattern['name'],
                    'type': 'attack_chain',
                    'severity': {'level': 5 if pattern['severity'] == 'critical' else 4, 'confidence': 0.90},
                    'findings': finding_objects,
                    'finding_count': len(finding_objects),
                    'correlation_type': 'attack_chain',
                    'description': f"Detected coordinated attack: {pattern['name']}",
                    'attack_stages': pattern['stages'],
                    'evidence': {
                        'pattern_matched': pattern['name'],
                        'stages_detected': [f['type'] for f in finding_objects]
                    }
                }
                
                incidents.append(incident)
                processed.update(finding_indices)
        
        return incidents
    
    def _correlate_temporal(self, findings: List[Dict[str, Any]], 
                           processed: Set[int]) -> List[Dict[str, Any]]:
        """Correlate findings by IP address and time window"""
        incidents = []
        
        # Group findings by IP address
        ip_findings = defaultdict(list)
        
        for i, finding in enumerate(findings):
            if i in processed:
                continue
            
            # Extract IP from evidence
            ip = None
            if 'evidence' in finding:
                ip = finding['evidence'].get('ip_address')
            
            if ip:
                ip_findings[ip].append((i, finding))
        
        # Create incidents for IPs with multiple findings in time window
        for ip, ip_finding_list in ip_findings.items():
            if len(ip_finding_list) < 2:
                continue
            
            # Sort by timestamp
            ip_finding_list.sort(key=lambda x: x[1].get('timestamp', ''))
            
            # Group findings within time window
            groups = []
            current_group = [ip_finding_list[0]]
            
            for i in range(1, len(ip_finding_list)):
                prev_finding = current_group[-1][1]
                curr_finding = ip_finding_list[i][1]
                
                # Check time difference
                time_diff = self._calculate_time_diff(
                    prev_finding.get('timestamp'),
                    curr_finding.get('timestamp')
                )
                
                if time_diff and time_diff <= self.time_window_minutes:
                    current_group.append(ip_finding_list[i])
                else:
                    if len(current_group) >= 2:
                        groups.append(current_group)
                    current_group = [ip_finding_list[i]]
            
            if len(current_group) >= 2:
                groups.append(current_group)
            
            # Create incidents for each group
            for group in groups:
                finding_indices = [idx for idx, _ in group]
                finding_objects = [f for _, f in group]
                
                # Determine severity based on finding types
                max_severity = max(
                    self._severity_to_level(f.get('severity', 'low'))
                    for f in finding_objects
                )
                
                incident = {
                    'title': f'Coordinated Attack from {ip}',
                    'type': 'temporal_correlation',
                    'severity': {'level': max_severity, 'confidence': 0.85},
                    'findings': finding_objects,
                    'finding_count': len(finding_objects),
                    'correlation_type': 'temporal',
                    'description': f'Multiple security events from same IP within {self.time_window_minutes} minutes',
                    'evidence': {
                        'ip_address': ip,
                        'time_window_minutes': self.time_window_minutes,
                        'finding_types': [f['type'] for f in finding_objects]
                    }
                }
                
                incidents.append(incident)
                processed.update(finding_indices)
        
        return incidents
    
    def _correlate_credentials(self, findings: List[Dict[str, Any]], 
                               processed: Set[int]) -> List[Dict[str, Any]]:
        """Correlate findings related to same credentials"""
        incidents = []
        
        # Group findings by credential/secret type
        credential_findings = defaultdict(list)
        
        for i, finding in enumerate(findings):
            if i in processed:
                continue
            
            if finding.get('type') in ['secret_leak', 'high_entropy_string']:
                # Extract credential identifier
                pattern_id = finding.get('pattern_id', 'unknown')
                credential_findings[pattern_id].append((i, finding))
        
        # Create incidents for credential groups
        for cred_type, cred_finding_list in credential_findings.items():
            if len(cred_finding_list) >= 2:
                finding_indices = [idx for idx, _ in cred_finding_list]
                finding_objects = [f for _, f in cred_finding_list]
                
                incident = {
                    'title': f'Multiple {cred_type} Credentials Exposed',
                    'type': 'credential_correlation',
                    'severity': {'level': 4, 'confidence': 0.90},
                    'findings': finding_objects,
                    'finding_count': len(finding_objects),
                    'correlation_type': 'credential',
                    'description': f'Multiple instances of {cred_type} found in codebase',
                    'evidence': {
                        'credential_type': cred_type,
                        'locations': [f.get('file_path') for f in finding_objects]
                    }
                }
                
                incidents.append(incident)
                processed.update(finding_indices)
        
        return incidents
    
    def _correlate_targets(self, findings: List[Dict[str, Any]], 
                          processed: Set[int]) -> List[Dict[str, Any]]:
        """Correlate findings targeting same resource"""
        incidents = []
        
        # Group findings by target (file, endpoint, table)
        target_findings = defaultdict(list)
        
        for i, finding in enumerate(findings):
            if i in processed:
                continue
            
            # Identify target
            target = finding.get('file_path')
            if not target and 'evidence' in finding:
                target = finding['evidence'].get('endpoint') or finding['evidence'].get('table')
            
            if target:
                target_findings[target].append((i, finding))
        
        # Create incidents for targets with multiple findings
        for target, target_finding_list in target_findings.items():
            if len(target_finding_list) >= 3:  # At least 3 findings on same target
                finding_indices = [idx for idx, _ in target_finding_list]
                finding_objects = [f for _, f in target_finding_list]
                
                max_severity = max(
                    self._severity_to_level(f.get('severity', 'low'))
                    for f in finding_objects
                )
                
                incident = {
                    'title': f'Multiple Vulnerabilities in {target}',
                    'type': 'target_correlation',
                    'severity': {'level': max_severity, 'confidence': 0.80},
                    'findings': finding_objects,
                    'finding_count': len(finding_objects),
                    'correlation_type': 'target',
                    'description': f'Multiple security issues found in same target: {target}',
                    'evidence': {
                        'target': target,
                        'vulnerability_types': [f['type'] for f in finding_objects]
                    }
                }
                
                incidents.append(incident)
                processed.update(finding_indices)
        
        return incidents
    
    def _create_single_finding_incident(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """Create an incident from a single finding"""
        severity_level = self._severity_to_level(finding.get('severity', 'low'))
        
        return {
            'title': finding.get('name', 'Security Finding'),
            'type': 'single_finding',
            'severity': {'level': severity_level, 'confidence': finding.get('confidence', 0.75)},
            'findings': [finding],
            'finding_count': 1,
            'correlation_type': 'none',
            'description': finding.get('description', 'Security issue detected'),
            'evidence': finding.get('evidence', {})
        }
    
    def _severity_to_level(self, severity: str) -> int:
        """Convert severity string to numeric level"""
        severity_map = {
            'critical': 5,
            'high': 4,
            'medium': 3,
            'low': 2,
            'informational': 1
        }
        return severity_map.get(severity.lower(), 2)
    
    def _calculate_time_diff(self, timestamp1: str, timestamp2: str) -> float:
        """Calculate time difference in minutes"""
        try:
            if not timestamp1 or not timestamp2:
                return None
            
            t1 = datetime.fromisoformat(timestamp1.replace('Z', '+00:00'))
            t2 = datetime.fromisoformat(timestamp2.replace('Z', '+00:00'))
            
            diff = abs((t2 - t1).total_seconds() / 60)
            return diff
        except:
            return None
    
    def get_correlation_summary(self, incidents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get correlation statistics"""
        from collections import Counter
        
        correlation_types = Counter(i['correlation_type'] for i in incidents)
        severity_levels = Counter(i['severity']['level'] for i in incidents)
        
        total_findings = sum(i['finding_count'] for i in incidents)
        
        return {
            'total_incidents': len(incidents),
            'total_findings': total_findings,
            'correlation_types': dict(correlation_types),
            'severity_distribution': dict(severity_levels),
            'average_findings_per_incident': total_findings / len(incidents) if incidents else 0
        }

# Made with Bob
