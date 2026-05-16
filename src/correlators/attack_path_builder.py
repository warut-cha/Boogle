"""
Attack Path Builder
Constructs attack path graphs showing how security findings connect into attack chains
"""

from typing import Dict, Any, List, Set, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class AttackPathBuilder:
    """Builds attack path graphs from correlated findings"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize attack path builder
        
        Args:
            config: Configuration dictionary (optional)
        """
        self.config = config or {}
    
    def build_attack_path(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build attack path graph for an incident
        
        Args:
            incident: Incident dictionary with findings
            
        Returns:
            Attack path dictionary with nodes and edges
        """
        findings = incident.get('findings', [])
        
        if not findings:
            return {'nodes': [], 'edges': []}
        
        # Detect attack pattern
        pattern = self._detect_attack_pattern(findings)
        
        if pattern:
            logger.info(f"Detected attack pattern: {pattern['name']}")
            return self._build_pattern_graph(pattern, findings)
        
        # Build generic graph if no pattern detected
        return self._build_generic_graph(findings)
    
    def _detect_attack_pattern(self, findings: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Detect known attack patterns from findings"""
        finding_types = set(f.get('finding_type') for f in findings)
        
        # Demo scenario: Credential leakage through abandoned export API
        if self._matches_demo_scenario(findings):
            return {
                'name': 'credential_leakage_abandoned_api',
                'title': 'Credential Leakage Through Abandoned Export API',
                'stages': [
                    {
                        'id': 'secret',
                        'label': 'Hardcoded API Key',
                        'type': 'secret',
                        'finding_types': ['hardcoded_secret']
                    },
                    {
                        'id': 'old_api',
                        'label': 'Abandoned Export API',
                        'type': 'api',
                        'finding_types': ['deprecated_api']
                    },
                    {
                        'id': 'traffic',
                        'label': 'Suspicious Requests',
                        'type': 'runtime',
                        'finding_types': ['runtime_anomaly']
                    },
                    {
                        'id': 'db',
                        'label': 'Users Table Read Spike',
                        'type': 'database',
                        'finding_types': ['database_anomaly']
                    },
                    {
                        'id': 'leak',
                        'label': 'Possible Data Leak',
                        'type': 'impact',
                        'finding_types': []
                    }
                ],
                'edges': [
                    {'from': 'secret', 'to': 'old_api', 'label': 'used by'},
                    {'from': 'old_api', 'to': 'traffic', 'label': 'targeted by'},
                    {'from': 'traffic', 'to': 'db', 'label': 'accesses'},
                    {'from': 'db', 'to': 'leak', 'label': 'may expose'}
                ]
            }
        
        # SQL Injection to Data Breach
        if 'sql_injection_attempt' in finding_types and 'database_anomaly' in finding_types:
            return {
                'name': 'sql_injection_breach',
                'title': 'SQL Injection to Data Breach',
                'stages': [
                    {'id': 'injection', 'label': 'SQL Injection', 'type': 'vulnerability', 'finding_types': ['sql_injection_attempt']},
                    {'id': 'db_access', 'label': 'Database Access', 'type': 'database', 'finding_types': ['database_anomaly']},
                    {'id': 'exfiltration', 'label': 'Data Exfiltration', 'type': 'impact', 'finding_types': []}
                ],
                'edges': [
                    {'from': 'injection', 'to': 'db_access', 'label': 'exploits'},
                    {'from': 'db_access', 'to': 'exfiltration', 'label': 'enables'}
                ]
            }
        
        # Credential Theft Chain
        if 'hardcoded_secret' in finding_types and 'runtime_anomaly' in finding_types:
            return {
                'name': 'credential_theft',
                'title': 'Credential Theft and Abuse',
                'stages': [
                    {'id': 'secret', 'label': 'Exposed Credential', 'type': 'secret', 'finding_types': ['hardcoded_secret']},
                    {'id': 'abuse', 'label': 'Credential Abuse', 'type': 'runtime', 'finding_types': ['runtime_anomaly']},
                    {'id': 'impact', 'label': 'Unauthorized Access', 'type': 'impact', 'finding_types': []}
                ],
                'edges': [
                    {'from': 'secret', 'to': 'abuse', 'label': 'enables'},
                    {'from': 'abuse', 'to': 'impact', 'label': 'results in'}
                ]
            }
        
        return None
    
    def _matches_demo_scenario(self, findings: List[Dict[str, Any]]) -> bool:
        """Check if findings match the demo scenario pattern"""
        finding_types = set(f.get('finding_type') for f in findings)
        
        # Must have hardcoded secret and deprecated API
        has_secret = 'hardcoded_secret' in finding_types
        has_deprecated_api = 'deprecated_api' in finding_types
        
        # Should have runtime or database anomaly
        has_runtime = 'runtime_anomaly' in finding_types
        has_db = 'database_anomaly' in finding_types
        
        # Check for export endpoint
        has_export_endpoint = any(
            '/export' in str(f.get('endpoint', '')).lower() or
            'export' in str(f.get('file', '')).lower()
            for f in findings
        )
        
        return has_secret and has_deprecated_api and (has_runtime or has_db) and has_export_endpoint
    
    def _build_pattern_graph(self, pattern: Dict[str, Any], 
                            findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build attack path graph from detected pattern"""
        nodes = []
        edges = pattern['edges']
        
        # Create nodes from pattern stages
        for stage in pattern['stages']:
            node = {
                'id': stage['id'],
                'label': stage['label'],
                'type': stage['type']
            }
            
            # Find matching findings for this stage
            matching_findings = []
            for finding in findings:
                if finding.get('finding_type') in stage['finding_types']:
                    matching_findings.append(finding)
            
            # Add finding details to node
            if matching_findings:
                node['findings'] = [f.get('finding_id') for f in matching_findings]
                node['evidence'] = [f.get('evidence') for f in matching_findings if f.get('evidence')]
                
                # Add specific details based on finding type
                for finding in matching_findings:
                    if finding.get('file'):
                        node['file'] = finding['file']
                    if finding.get('endpoint'):
                        node['endpoint'] = finding['endpoint']
                    if finding.get('database_table'):
                        node['database_table'] = finding['database_table']
            
            nodes.append(node)
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    def _build_generic_graph(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build generic attack path when no pattern is detected"""
        nodes = []
        edges = []
        
        # Group findings by category
        categories = {}
        for finding in findings:
            category = finding.get('category', 'unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append(finding)
        
        # Create nodes for each category
        node_ids = []
        for i, (category, cat_findings) in enumerate(categories.items()):
            node_id = f"node_{i}"
            node_ids.append(node_id)
            
            # Create label from category
            label = self._category_to_label(category)
            
            node = {
                'id': node_id,
                'label': label,
                'type': category,
                'findings': [f.get('finding_id') for f in cat_findings],
                'finding_count': len(cat_findings)
            }
            
            nodes.append(node)
        
        # Create sequential edges
        for i in range(len(node_ids) - 1):
            edges.append({
                'from': node_ids[i],
                'to': node_ids[i + 1],
                'label': 'leads to'
            })
        
        # Add impact node if we have multiple findings
        if len(findings) >= 2:
            impact_node = {
                'id': 'impact',
                'label': 'Security Impact',
                'type': 'impact'
            }
            nodes.append(impact_node)
            
            if node_ids:
                edges.append({
                    'from': node_ids[-1],
                    'to': 'impact',
                    'label': 'results in'
                })
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    def _category_to_label(self, category: str) -> str:
        """Convert category to human-readable label"""
        labels = {
            'secret_exposure': 'Exposed Secrets',
            'legacy_api': 'Legacy API',
            'runtime_behavior': 'Runtime Anomaly',
            'database_activity': 'Database Activity',
            'infrastructure': 'Infrastructure Risk',
            'logging': 'Logging Issue',
            'unknown': 'Security Finding'
        }
        return labels.get(category, category.replace('_', ' ').title())
    
    def visualize_attack_path(self, attack_path: Dict[str, Any]) -> str:
        """
        Generate ASCII visualization of attack path
        
        Args:
            attack_path: Attack path dictionary
            
        Returns:
            ASCII art representation
        """
        nodes = attack_path.get('nodes', [])
        edges = attack_path.get('edges', [])
        
        if not nodes:
            return "No attack path available"
        
        # Build simple text representation
        lines = ["Attack Path:", ""]
        
        # Create node lookup
        node_map = {n['id']: n for n in nodes}
        
        # Build path by following edges
        visited = set()
        current = nodes[0]['id']
        
        while current and current not in visited:
            visited.add(current)
            node = node_map.get(current)
            
            if node:
                lines.append(f"  [{node['type'].upper()}] {node['label']}")
                
                # Find next edge
                next_edge = next((e for e in edges if e['from'] == current), None)
                if next_edge:
                    lines.append(f"      ↓ {next_edge['label']}")
                    current = next_edge['to']
                else:
                    current = None
        
        return "\n".join(lines)


# Made with Bob