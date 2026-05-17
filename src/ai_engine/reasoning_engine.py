"""
AI Reasoning Engine
Integrates IBM Bob (watsonx.ai) for AI-powered security analysis
"""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ReasoningEngine:
    """AI reasoning engine powered by IBM Bob for enhanced security analysis"""
    
    def __init__(self, config: Dict[str, Any], memory_manager=None):
        """Initialize reasoning engine"""
        self.config = config
        self.local_models_enabled = config.get('local_models', {}).get('enabled', True)
        self.bob_enabled = config.get('bob', {}).get('enabled', True)
        self._memory_manager_ref = memory_manager  # JSON memory fallback
        
        # Initialize Bob client
        self.bob_client = None
        if self.bob_enabled:
            self._init_bob_client()
        
        # Initialize vector memory
        self.vector_memory = None
        if config.get('vector_memory', {}).get('enabled', True):
            self._init_vector_memory()
    
    def _init_bob_client(self):
        """Initialize IBM Bob client"""
        try:
            from .bob_client import BobClient
            
            bob_config = self.config.get('bob', {})
            self.bob_client = BobClient(bob_config)
            
            health = self.bob_client.health_check()
            if health.get('enabled'):
                logger.info("IBM Bob client initialized successfully")
            else:
                logger.warning("IBM Bob client not fully enabled")
                self.bob_enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize IBM Bob client: {str(e)}")
            self.bob_enabled = False
            self.bob_client = None
    
    def _init_vector_memory(self):
        """Initialize vector memory"""
        try:
            from .vector_memory import VectorMemory
            
            vector_config = self.config.get('vector_memory', {})
            self.vector_memory = VectorMemory(vector_config)
            
            stats = self.vector_memory.get_statistics()
            logger.info(f"Vector memory initialized: {stats.get('total_entries', 0)} entries")
        except Exception as e:
            logger.error(f"Failed to initialize vector memory: {str(e)}")
            self.vector_memory = None
    
    def enhance_analysis(self, incidents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhance incident analysis with AI reasoning using IBM Bob
        
        Args:
            incidents: List of incidents
            
        Returns:
            Enhanced incidents with Bob AI analysis
        """
        logger.info(f"Enhancing analysis for {len(incidents)} incidents with IBM Bob")
        
        enhanced_incidents = []
        
        for incident in incidents:
            enhanced = incident.copy()
            
            # Get Bob analysis
            if self.bob_enabled and self.bob_client:
                bob_output = self._get_bob_analysis(incident)
                enhanced['bob_analysis'] = bob_output
                
                # Store in vector memory for future reference
                if self.vector_memory and bob_output.get('ai_memory'):
                    try:
                        self.vector_memory.add_incident_memory(incident, bob_output['ai_memory'])
                    except Exception as e:
                        logger.warning(f"Failed to store in vector memory: {str(e)}")
            
            # Add local insights as fallback
            if self.local_models_enabled:
                enhanced['ai_insights'] = self._generate_local_insights(incident)
            
            # Add risk assessment
            enhanced['risk_assessment'] = self._assess_risk(incident)
            
            # Add attack attribution
            enhanced['attack_attribution'] = self._attribute_attack(incident)
            
            enhanced_incidents.append(enhanced)
        
        return enhanced_incidents
    
    def _get_bob_analysis(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get analysis from IBM Bob
        
        Args:
            incident: Incident to analyze
            
        Returns:
            Bob output with analysis, fixes, tests, report, etc.
        """
        try:
            # Search for similar past incidents
            related_memory = []
            
            # Try ChromaDB vector search first
            if self.vector_memory:
                try:
                    similar = self.vector_memory.search_similar_incidents(incident, n_results=3)
                    related_memory = similar
                    logger.info(f"Vector memory: found {len(related_memory)} similar incidents")
                except Exception as e:
                    logger.warning(f"Vector memory search failed: {e}")
            
            # Fall back to JSON keyword search if vector search yielded nothing
            if not related_memory and self._memory_manager_ref:
                try:
                    json_similar = self._memory_manager_ref.search_similar(incident, max_results=3)
                    related_memory = json_similar
                    if json_similar:
                        logger.info(f"JSON memory fallback: found {len(json_similar)} similar patterns")
                except Exception as e:
                    logger.warning(f"JSON memory search failed: {e}")
            
            # Build Bob input
            bob_input = {
                'incident': incident,
                'attack_path': incident.get('attack_path', {}),
                'confidence': {
                    'score': incident.get('confidence_score', 0.75),
                    'reasons': incident.get('confidence_reasons', []),
                    'limitations': incident.get('confidence_limitations', [])
                },
                'related_memory': related_memory,
                'requested_outputs': [
                    'attack_explanation',
                    'target_analysis',
                    'fix_plan',
                    'security_tests',
                    'incident_report',
                    'ai_memory',
                    'pr_draft'
                ]
            }
            
            # Get Bob analysis
            bob_output = self.bob_client.analyze_incident(bob_input)
            
            return bob_output
        except Exception as e:
            logger.error(f"Failed to get Bob analysis: {str(e)}")
            return {}
    
    def _generate_local_insights(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights using local ML models"""
        findings = incident.get('findings', [])
        correlation_type = incident.get('correlation_type', 'none')
        
        insights = {
            'attack_sophistication': self._assess_sophistication(incident),
            'likely_attacker_profile': self._profile_attacker(incident),
            'attack_stage': self._identify_attack_stage(incident),
            'recommended_priority': self._calculate_priority(incident)
        }
        
        return insights
    
    
    def _assess_risk(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall risk"""
        severity = incident.get('severity', 3)
        if isinstance(severity, dict):
            severity_level = severity.get('level', 3)
        else:
            severity_level = incident.get('severity_level', 3)
        
        finding_count = incident.get('finding_count', len(incident.get('findings', [])))
        correlation_type = incident.get('correlation_type', 'none')
        
        # Calculate risk score
        risk_score = severity_level * 0.4
        
        if correlation_type == 'attack_chain':
            risk_score += 2.0
        elif correlation_type == 'temporal':
            risk_score += 1.0
        
        if finding_count >= 5:
            risk_score += 1.0
        elif finding_count >= 3:
            risk_score += 0.5
        
        risk_score = min(5.0, risk_score)
        
        risk_level = 'Critical' if risk_score >= 4.5 else \
                     'High' if risk_score >= 3.5 else \
                     'Medium' if risk_score >= 2.5 else \
                     'Low'
        
        return {
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'business_impact': self._assess_business_impact(incident),
            'data_at_risk': self._identify_data_at_risk(incident)
        }
    
    def _assess_sophistication(self, incident: Dict[str, Any]) -> str:
        """Assess attack sophistication"""
        correlation_type = incident.get('correlation_type', 'none')
        finding_count = incident.get('finding_count', 0)
        
        if correlation_type == 'attack_chain' and finding_count >= 4:
            return 'Advanced - Multi-stage coordinated attack'
        elif correlation_type == 'temporal' and finding_count >= 3:
            return 'Intermediate - Coordinated exploitation'
        elif finding_count >= 2:
            return 'Basic - Opportunistic attack'
        else:
            return 'Low - Single vulnerability exploitation'
    
    def _profile_attacker(self, incident: Dict[str, Any]) -> str:
        """Profile likely attacker"""
        findings = incident.get('findings', [])
        finding_types = [f.get('finding_type') for f in findings]
        
        if 'large_data_export' in finding_types and 'privilege_escalation' in finding_types:
            return 'Insider threat or advanced persistent threat (APT)'
        elif 'sql_injection_attempt' in finding_types or 'command_injection' in finding_types:
            return 'External attacker with technical skills'
        elif 'brute_force_attack' in finding_types:
            return 'Automated attack or script kiddie'
        else:
            return 'Unknown - requires further investigation'
    
    def _identify_attack_stage(self, incident: Dict[str, Any]) -> str:
        """Identify current attack stage"""
        findings = incident.get('findings', [])
        finding_types = [f.get('finding_type') for f in findings]
        
        if 'large_data_export' in finding_types:
            return 'Exfiltration - Data being stolen'
        elif 'privilege_escalation' in finding_types:
            return 'Privilege Escalation - Gaining higher access'
        elif 'sql_injection_attempt' in finding_types or 'command_injection' in finding_types:
            return 'Exploitation - Attempting to compromise system'
        elif 'deprecated_api_access' in finding_types:
            return 'Reconnaissance - Probing for vulnerabilities'
        else:
            return 'Initial Access - Attempting entry'
    
    def _calculate_priority(self, incident: Dict[str, Any]) -> str:
        """Calculate remediation priority"""
        severity = incident.get('severity', 3)
        if isinstance(severity, dict):
            severity_level = severity.get('level', 3)
        else:
            severity_level = incident.get('severity_level', 3)
        
        if severity_level >= 5:
            return 'P0 - Immediate (within 1 hour)'
        elif severity_level >= 4:
            return 'P1 - Urgent (within 24 hours)'
        elif severity_level >= 3:
            return 'P2 - High (within 1 week)'
        elif severity_level >= 2:
            return 'P3 - Medium (within 1 month)'
        else:
            return 'P4 - Low (next quarter)'
    
    def _assess_business_impact(self, incident: Dict[str, Any]) -> str:
        """Assess business impact"""
        findings = incident.get('findings', [])
        finding_types = [f.get('finding_type') for f in findings]
        
        if 'large_data_export' in finding_types or 'sensitive_data_in_logs' in finding_types:
            return 'High - Potential data breach and regulatory violations'
        elif 'secret_leak' in finding_types:
            return 'High - Compromised credentials could lead to further breaches'
        elif 'missing_authentication' in finding_types:
            return 'Medium - Unauthorized access to sensitive resources'
        else:
            return 'Low - Limited immediate business impact'
    
    def _identify_data_at_risk(self, incident: Dict[str, Any]) -> List[str]:
        """Identify what data is at risk"""
        findings = incident.get('findings', [])
        data_at_risk = set()
        
        for finding in findings:
            description = finding.get('description', '').lower()
            evidence = str(finding.get('evidence', {})).lower()
            
            if 'payment' in description or 'card' in description:
                data_at_risk.add('Payment card data')
            if 'customer' in description or 'user' in description:
                data_at_risk.add('Customer personal information')
            if 'password' in description or 'credential' in description:
                data_at_risk.add('Authentication credentials')
            if 'database' in description:
                data_at_risk.add('Database contents')
            if 'api' in description or 'key' in description:
                data_at_risk.add('API keys and secrets')
        
        return list(data_at_risk) if data_at_risk else ['System integrity']
    
    def _attribute_attack(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Attribute attack characteristics"""
        evidence = incident.get('evidence', {})
        source_ip = 'Unknown'
        if isinstance(evidence, dict):
            source_ip = evidence.get('ip_address', 'Unknown')
        
        return {
            'source_ip': source_ip,
            'attack_vector': self._identify_attack_vector(incident),
            'tools_used': self._identify_tools(incident),
            'indicators_of_compromise': self._extract_iocs(incident)
        }
    
    def _identify_attack_vector(self, incident: Dict[str, Any]) -> str:
        """Identify primary attack vector"""
        findings = incident.get('findings', [])
        finding_types = [f.get('finding_type') for f in findings]
        
        if 'sql_injection_attempt' in finding_types:
            return 'SQL Injection'
        elif 'command_injection' in finding_types:
            return 'Command Injection'
        elif 'deprecated_api' in finding_types:
            return 'Deprecated API Exploitation'
        elif 'missing_authentication' in finding_types:
            return 'Authentication Bypass'
        else:
            return 'Multiple vectors'
    
    def _identify_tools(self, incident: Dict[str, Any]) -> List[str]:
        """Identify likely tools used"""
        findings = incident.get('findings', [])
        tools = []
        
        for finding in findings:
            if finding.get('type') == 'sql_injection_attempt':
                tools.append('SQLMap or similar SQL injection tool')
            elif finding.get('type') == 'brute_force_attack':
                tools.append('Hydra or similar brute force tool')
            elif finding.get('type') == 'rapid_requests':
                tools.append('Automated scanner or bot')
        
        return tools if tools else ['Manual exploitation or unknown tools']
    
    def _extract_iocs(self, incident: Dict[str, Any]) -> List[str]:
        """Extract indicators of compromise"""
        iocs = []
        evidence = incident.get('evidence', {})
        
        if isinstance(evidence, dict) and 'ip_address' in evidence:
            iocs.append(f"IP: {evidence['ip_address']}")
        
        findings = incident.get('findings', [])
        for finding in findings:
            if finding.get('type') == 'secret_leak':
                iocs.append(f"Leaked credential in {finding.get('file_path')}")
        
        return iocs if iocs else ['No specific IOCs identified']

# Made with Bob
