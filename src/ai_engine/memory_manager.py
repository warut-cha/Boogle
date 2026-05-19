"""
AI Memory Manager
Stores and retrieves security prevention rules learned from incidents
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages AI security memory for continuous learning"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize memory manager
        
        Args:
            config: Memory configuration
        """
        self.config = config
        self.storage_path = Path(config.get('storage_path', './models/ai_memory.json'))
        self.max_entries = config.get('max_entries', 1000)
        self.auto_learn = config.get('auto_learn', True)
        self.memory: List[Dict[str, Any]] = []
        
        # Create storage directory if needed
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing memory
        self._load_memory()
    
    def _load_memory(self):
        """Load memory from storage"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    self.memory = json.load(f)
                logger.info(f"Loaded {len(self.memory)} memory entries")
            except Exception as e:
                logger.error(f"Failed to load memory: {str(e)}")
                self.memory = []
        else:
            self.memory = []
            logger.info("No existing memory found, starting fresh")
    
    def _save_memory(self):
        """Save memory to storage"""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.memory, f, indent=2)
            logger.info(f"Saved {len(self.memory)} memory entries")
        except Exception as e:
            logger.error(f"Failed to save memory: {str(e)}")
    
    def learn_from_incidents(self, incidents: List[Dict[str, Any]]):
        """
        Learn prevention rules from incidents
        
        Args:
            incidents: List of security incidents
        """
        if not self.auto_learn:
            logger.info("Auto-learn disabled, skipping memory update")
            return
        
        logger.info(f"Learning from {len(incidents)} incidents")
        
        for incident in incidents:
            memory_entry = self._create_memory_entry(incident)
            if memory_entry:
                self.add_memory(memory_entry)
        
        self._save_memory()
    
    def _create_memory_entry(self, incident: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create memory entry from incident"""
        findings = incident.get('findings', [])
        
        if not findings:
            return None
        
        # Extract incident pattern
        incident_pattern = self._extract_incident_pattern(incident)
        
        # Determine root cause
        root_cause = self._determine_root_cause(incident)
        
        # Identify signals to watch
        signals = self._identify_signals(incident)
        
        # Generate prevention rule
        prevention_rule = self._generate_prevention_rule(incident)
        
        # Generate recommended tests
        recommended_tests = self._generate_tests(incident)
        
        # Determine escalation conditions
        escalation_conditions = self._determine_escalation_conditions(incident)
        
        memory_entry = {
            'memory_type': 'security_prevention_rule',
            'incident_pattern': incident_pattern,
            'root_cause': root_cause,
            'signals_to_watch': signals,
            'prevention_rule': prevention_rule,
            'recommended_tests': recommended_tests,
            'severity_escalation_conditions': escalation_conditions,
            'created_at': datetime.now().isoformat(),
            'incident_id': incident.get('id') or incident.get('incident_id'),
            'severity_level': self._extract_severity_level(incident)
        }
        
    
    def _extract_severity_level(self, incident: Dict[str, Any]) -> int:
        """
        Extract severity level from incident, handling different formats.
        
        Args:
            incident: Incident dictionary
            
        Returns:
            Severity level as integer (1-5), defaults to 3
        """
        # First check for direct severity_level field
        if 'severity_level' in incident:
            level = incident['severity_level']
            if isinstance(level, int):
                return level
        
        # Check if severity is a dict with level
        severity = incident.get('severity')
        if isinstance(severity, dict):
            level = severity.get('level', 3)
            if isinstance(level, int):
                return level
        
        # If severity is a string, map it to a level
        if isinstance(severity, str):
            severity_map = {
                'critical': 5,
                'high': 4,
                'medium': 3,
                'low': 2,
                'info': 1,
                'informational': 1
            }
            return severity_map.get(severity.lower(), 3)
        
        # Default to medium severity
        return 3
        return memory_entry
    
    def _get_value(self, item, key, default=None):
        """Safely read from dicts or objects."""
        if isinstance(item, dict):
            return item.get(key, default)

        return getattr(item, key, default)


    def _extract_incident_pattern(self, incident) -> str:
        """Extract a stable incident pattern from an incident."""

        findings = self._get_value(incident, "findings", [])

        finding_types: list[str] = []

        for finding in findings:
            finding_type = (
                self._get_value(finding, "finding_type")
                or self._get_value(finding, "type")
                or self._get_value(finding, "category")
            )

            if finding_type is None:
                continue

            finding_types.append(str(finding_type))

        if not finding_types:
            title = self._get_value(incident, "title")
            if title:
                return str(title)

            severity = self._get_value(incident, "severity", "unknown")
            return f"unknown_incident_pattern_{severity}"

        unique_types = sorted(set(finding_types))

        if len(unique_types) == 1:
            return unique_types[0]

        return f"Coordinated attack chain involving: {', '.join(unique_types)}"
    def _determine_root_cause(self, incident: Dict[str, Any]) -> str:
        """Determine root cause of incident"""
        findings = incident.get('findings', [])
        finding_types = [f.get('type') for f in findings]
        
        # Common root causes
        if 'secret_leak' in finding_types:
            return "Hardcoded credentials in source code without proper secret management"
        elif 'sql_injection_attempt' in finding_types or 'vulnerability' in finding_types:
            return "Insufficient input validation and sanitization"
        elif 'missing_authentication' in finding_types:
            return "Lack of authentication requirements on sensitive endpoints"
        elif 'deprecated_api' in finding_types:
            return "Failure to remove or properly deprecate old API versions"
        elif 'command_injection' in finding_types:
            return "Unsafe command execution without input validation"
        elif 'cors_misconfiguration' in finding_types:
            return "Overly permissive CORS configuration"
        else:
            return "Security misconfiguration or insufficient security controls"
    
    def _identify_signals(self, incident: Dict[str, Any]) -> List[str]:
        """Identify signals that indicate this type of incident"""
        findings = incident.get('findings', [])
        signals = []
        
        for finding in findings:
            finding_type = finding.get('type')
            
            if finding_type == 'secret_leak':
                signals.append("High-entropy strings in configuration files")
                signals.append("API key patterns in source code")
                signals.append("Credentials in environment variable assignments")
            elif finding_type == 'sql_injection_attempt':
                signals.append("SQL keywords in user input")
                signals.append("String concatenation in database queries")
                signals.append("Unparameterized query execution")
            elif finding_type == 'deprecated_api':
                signals.append("Old API version patterns in routes")
                signals.append("@deprecated markers in code")
                signals.append("Legacy endpoint access in logs")
            elif finding_type == 'missing_authentication':
                signals.append("Route definitions without auth decorators")
                signals.append("Sensitive endpoints without access control")
            elif finding_type == 'large_data_export':
                signals.append("High-volume data queries")
                signals.append("Export operations without rate limiting")
                signals.append("Bulk data access from single source")
        
        # Remove duplicates and limit
        return list(set(signals))[:5]
    
    def _generate_prevention_rule(self, incident: Dict[str, Any]) -> str:
        """Generate actionable prevention rule"""
        findings = incident.get('findings', [])
        finding_types = [f.get('type') for f in findings]
        
        if 'secret_leak' in finding_types:
            return "Implement pre-commit hooks to scan for secrets, use environment variables or secret management services, rotate exposed credentials immediately"
        elif 'sql_injection_attempt' in finding_types:
            return "Always use parameterized queries or ORM, implement input validation, enable SQL injection detection in WAF"
        elif 'deprecated_api' in finding_types:
            return "Implement API versioning policy with sunset dates, return 410 Gone for deprecated endpoints, provide migration documentation"
        elif 'missing_authentication' in finding_types:
            return "Require authentication on all non-public endpoints, implement role-based access control, audit endpoint security regularly"
        elif 'command_injection' in finding_types:
            return "Avoid shell command execution, use safe APIs, validate and sanitize all inputs, implement allowlists for commands"
        elif 'brute_force_attack' in finding_types:
            return "Implement rate limiting, account lockout after failed attempts, CAPTCHA for authentication, monitor for suspicious patterns"
        else:
            return "Review and strengthen security controls, implement defense in depth, conduct regular security audits"
    
    def _generate_tests(self, incident: Dict[str, Any]) -> List[str]:
        """Generate recommended security tests"""
        findings = incident.get('findings', [])
        finding_types = [f.get('type') for f in findings]
        tests = []
        
        if 'secret_leak' in finding_types:
            tests.append("Test: Scan all files for hardcoded secrets using regex patterns")
            tests.append("Test: Verify environment variables are used for sensitive config")
            tests.append("Test: Check that .env files are in .gitignore")
        
        if 'sql_injection_attempt' in finding_types or 'vulnerability' in finding_types:
            tests.append("Test: Verify all database queries use parameterized statements")
            tests.append("Test: Attempt SQL injection on all input fields")
            tests.append("Test: Check that ORM is used consistently")
        
        if 'deprecated_api' in finding_types:
            tests.append("Test: Verify deprecated endpoints return 410 Gone status")
            tests.append("Test: Check that old API versions are not accessible")
            tests.append("Test: Validate API version migration documentation exists")
        
        if 'missing_authentication' in finding_types:
            tests.append("Test: Verify all sensitive endpoints require authentication")
            tests.append("Test: Attempt to access protected resources without credentials")
            tests.append("Test: Check that authorization is enforced for role-specific actions")
        
        return tests[:5]  # Limit to 5 tests
    
    def _determine_escalation_conditions(self, incident: Dict[str, Any]) -> List[str]:
        """Determine conditions that increase severity"""
        conditions = []
        
        findings = incident.get('findings', [])
        finding_types = [f.get('type') for f in findings]
        
        if 'secret_leak' in finding_types:
            conditions.append("Credentials are actively being used in logs")
            conditions.append("Multiple credential types exposed in same codebase")
        
        if any(t in finding_types for t in ['sql_injection_attempt', 'command_injection']):
            conditions.append("Exploitation attempts detected in logs")
            conditions.append("Successful exploitation confirmed")
        
        if 'large_data_export' in finding_types:
            conditions.append("Data export volume exceeds normal baseline by 10x")
            conditions.append("Export occurs outside business hours")
        
        conditions.append("Multiple related incidents within short time window")
        conditions.append("Incident involves production environment")
        
        return conditions[:5]
    
    def add_memory(self, memory_entry: Dict[str, Any]):
        """Add memory entry"""
        # Check for duplicates
        if not self._is_duplicate(memory_entry):
            self.memory.append(memory_entry)
            
            # Enforce max entries
            if len(self.memory) > self.max_entries:
                # Remove oldest entries
                self.memory = sorted(
                    self.memory,
                    key=lambda x: x.get('created_at', ''),
                    reverse=True
                )[:self.max_entries]
            
            logger.info(f"Added memory entry: {memory_entry['incident_pattern'][:50]}...")
    
    def _is_duplicate(self, new_entry: Dict[str, Any]) -> bool:
        """Check if memory entry already exists"""
        new_pattern = new_entry.get('incident_pattern', '')
        
        for existing in self.memory:
            if existing.get('incident_pattern') == new_pattern:
                return True
        
        return False
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search memory entries"""
        query_lower = query.lower()
        results = []
        
        for entry in self.memory:
            # Search in pattern, root cause, and prevention rule
            searchable_text = (
                entry.get('incident_pattern', '').lower() +
                ' ' +
                entry.get('root_cause', '').lower() +
                ' ' +
                entry.get('prevention_rule', '').lower()
            )
            
            if query_lower in searchable_text:
                results.append(entry)
        
        return results
    
    def list_all(self) -> List[Dict[str, Any]]:
        """List all memory entries"""
        return self.memory
    
    def search_similar(self, incident: Dict[str, Any], max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Find similar past incidents from JSON memory using keyword overlap.
        Used as fallback when ChromaDB vector search is unavailable.
        
        Args:
            incident: Current incident to find similar patterns for
            max_results: Maximum number of results to return
            
        Returns:
            List of similar memory entries
        """
        try:
            all_memories = self.list_all()
            if not all_memories:
                return []
            
            # Build a keyword set from the current incident
            incident_keywords = self._extract_keywords(incident)
            
            if not incident_keywords:
                return []
            
            # Score each memory entry by keyword overlap
            scored = []
            for memory in all_memories:
                memory_keywords = self._extract_keywords_from_memory(memory)
                overlap = incident_keywords & memory_keywords
                if overlap:
                    score = len(overlap) / max(len(incident_keywords), 1)
                    scored.append((score, memory))
            
            # Return top matches above a minimum threshold
            scored.sort(key=lambda x: x[0], reverse=True)
            return [m for score, m in scored[:max_results] if score >= 0.15]
        except Exception as e:
            logger.warning(f"Error in search_similar: {e}")
            return []
    
    def _extract_keywords(self, incident: Dict[str, Any]) -> set:
        """Extract searchable keywords from an incident"""
        keywords = set()
        
        try:
            # Finding types
            for f in incident.get('findings', []):
                ft = f.get('finding_type') or f.get('type', '')
                if ft:
                    keywords.add(ft.lower())
            
            # Severity
            severity = incident.get('severity', '')
            if severity:
                keywords.add(severity.lower())
            
            # Affected assets — use stems not full paths
            for ep in incident.get('affected_endpoints', []):
                keywords.update(ep.lower().replace('/', ' ').split())
            for tbl in incident.get('affected_database_tables', []):
                keywords.add(tbl.lower())
            for f in incident.get('affected_files', []):
                keywords.add(Path(f).stem.lower())
            
            # Correlation type
            ct = incident.get('correlation_type', '')
            if ct:
                keywords.add(ct.lower())
            
            # Remove noise words
            noise_words = {'', 'api', 'the', 'and', 'for', 'v1', 'v2', 'v3'}
            return keywords - noise_words
        except Exception as e:
            logger.warning(f"Error extracting keywords: {e}")
            return set()
    
    def _extract_keywords_from_memory(self, memory: Dict[str, Any]) -> set:
        """Extract searchable keywords from a stored memory entry"""
        keywords = set()
        
        try:
            pattern = memory.get('incident_pattern', '')
            keywords.update(pattern.lower().replace('_', ' ').split())
            
            root_cause = memory.get('root_cause', '')
            keywords.update(root_cause.lower().split())
            
            for signal in memory.get('signals_to_watch', []):
                keywords.update(signal.lower().split())
            
            rule = memory.get('prevention_rule', '')
            keywords.update(rule.lower().split())
            
            # Remove noise words
            noise_words = {'', 'a', 'an', 'the', 'and', 'or', 'for', 'in',
                          'to', 'of', 'is', 'are', 'was', 'that', 'with'}
            return keywords - noise_words
        except Exception as e:
            logger.warning(f"Error extracting keywords from memory: {e}")
            return set()
    
    def export(self, output_path: str):
        """Export memory to file"""
        try:
            with open(output_path, 'w') as f:
                json.dump(self.memory, f, indent=2)
            logger.info(f"Exported memory to {output_path}")
        except Exception as e:
            logger.error(f"Failed to export memory: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics"""
        from collections import Counter
        
        severity_counts = Counter(m.get('severity_level', 3) for m in self.memory)
        
        return {
            'total_entries': len(self.memory),
            'by_severity': dict(severity_counts),
            'oldest_entry': min((m.get('created_at') for m in self.memory), default=None),
            'newest_entry': max((m.get('created_at') for m in self.memory), default=None)
        }

# Made with Bob
