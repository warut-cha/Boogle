"""
Deprecated API Detector
Identifies deprecated API endpoints, old unused APIs, and abandoned modules
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DeprecatedAPIDetector:
    """Detects deprecated APIs and abandoned code"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize deprecated API detector
        
        Args:
            config: Analysis configuration
        """
        self.config = config
        self.api_config = config.get('deprecated_api_detection', {})
        self.patterns = self._load_api_patterns()
        self.findings: List[Dict[str, Any]] = []
    
    def _load_api_patterns(self) -> Dict[str, Any]:
        """Load API detection patterns"""
        patterns_file = './patterns/api_patterns.json'
        
        try:
            with open(patterns_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load API patterns: {str(e)}")
            return {}
    
    def detect(self, code_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect deprecated APIs and abandoned code
        
        Args:
            code_data: Dictionary containing code files
            
        Returns:
            List of findings
        """
        self.findings = []
        
        files = code_data.get('files', [])
        
        for file_info in files:
            file_path = file_info['path']
            content = file_info['content']
            
            logger.info(f"Analyzing APIs in: {file_path}")
            
            # Detect deprecated API versions
            self._detect_deprecated_versions(file_path, content)
            
            # Detect deprecated decorators/markers
            self._detect_deprecated_markers(file_path, content)
            
            # Detect authentication issues
            self._detect_auth_issues(file_path, content)
            
            # Detect sensitive endpoints
            self._detect_sensitive_endpoints(file_path, content)
            
            # Detect CORS issues
            self._detect_cors_issues(file_path, content)
            
            # Detect abandoned code
            self._detect_abandoned_code(file_path, content)
        
        logger.info(f"Deprecated API detection complete. Found {len(self.findings)} issues.")
        return self.findings
    
    def _detect_deprecated_versions(self, file_path: str, content: str):
        """Detect deprecated API versions"""
        lines = content.split('\n')
        
        for pattern_info in self.patterns.get('deprecated_patterns', []):
            pattern = pattern_info['pattern']
            severity = pattern_info['severity']
            description = pattern_info['description']
            remediation = pattern_info['remediation']
            
            regex = re.compile(pattern, re.IGNORECASE)
            
            for line_num, line in enumerate(lines, start=1):
                if regex.search(line):
                    finding = {
                        'id': f"FINDING-{len(self.findings) + 1:04d}",
                        'type': 'deprecated_api',
                        'name': 'Deprecated API Version',
                        'severity': severity,
                        'confidence': 0.90,
                        'file_path': file_path,
                        'line_number': line_num,
                        'line_content': line.strip(),
                        'description': description,
                        'remediation': remediation,
                        'evidence': {
                            'pattern': pattern,
                            'matched_line': line.strip()
                        }
                    }
                    
                    self.findings.append(finding)
                    logger.warning(f"Deprecated API found in {file_path}:{line_num}")
    
    def _detect_deprecated_markers(self, file_path: str, content: str):
        """Detect @deprecated markers and comments"""
        lines = content.split('\n')
        
        deprecated_patterns = [
            r'@deprecated',
            r'@Deprecated',
            r'#\s*DEPRECATED',
            r'//\s*DEPRECATED',
            r'/\*\s*DEPRECATED'
        ]
        
        for line_num, line in enumerate(lines, start=1):
            for pattern in deprecated_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Look ahead to find the function/endpoint being deprecated
                    endpoint_name = self._extract_endpoint_name(lines, line_num)
                    
                    finding = {
                        'id': f"FINDING-{len(self.findings) + 1:04d}",
                        'type': 'deprecated_endpoint',
                        'name': 'Deprecated Endpoint Marker',
                        'severity': 'medium',
                        'confidence': 0.95,
                        'file_path': file_path,
                        'line_number': line_num,
                        'line_content': line.strip(),
                        'description': f'Endpoint marked as deprecated: {endpoint_name}',
                        'remediation': 'Remove deprecated endpoint or provide migration path',
                        'evidence': {
                            'marker': pattern,
                            'endpoint': endpoint_name
                        }
                    }
                    
                    self.findings.append(finding)
                    break
    
    def _detect_auth_issues(self, file_path: str, content: str):
        """Detect authentication and authorization issues"""
        lines = content.split('\n')
        
        # Pattern to detect routes without authentication
        route_pattern = r'@app\.route\([^)]+\)'
        auth_patterns = [
            r'@.*auth',
            r'@.*login_required',
            r'@.*require_auth',
            r'@.*authenticated'
        ]
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if this is a route definition
            if re.search(route_pattern, line):
                # Check next few lines for auth decorator
                has_auth = False
                for j in range(max(0, i - 3), min(len(lines), i + 3)):
                    for auth_pattern in auth_patterns:
                        if re.search(auth_pattern, lines[j], re.IGNORECASE):
                            has_auth = True
                            break
                    if has_auth:
                        break
                
                if not has_auth:
                    # Extract endpoint path
                    endpoint_match = re.search(r'["\']([^"\']+)["\']', line)
                    endpoint_path = endpoint_match.group(1) if endpoint_match else 'unknown'
                    
                    # Check if it's a sensitive endpoint
                    is_sensitive = any(
                        sensitive in endpoint_path.lower()
                        for sensitive in ['admin', 'user', 'payment', 'delete', 'update']
                    )
                    
                    if is_sensitive:
                        finding = {
                            'id': f"FINDING-{len(self.findings) + 1:04d}",
                            'type': 'missing_authentication',
                            'name': 'Endpoint Without Authentication',
                            'severity': 'high',
                            'confidence': 0.85,
                            'file_path': file_path,
                            'line_number': i + 1,
                            'line_content': line.strip(),
                            'description': f'Sensitive endpoint lacks authentication: {endpoint_path}',
                            'remediation': 'Add authentication decorator (@login_required, @auth.required, etc.)',
                            'evidence': {
                                'endpoint': endpoint_path,
                                'is_sensitive': is_sensitive
                            }
                        }
                        
                        self.findings.append(finding)
            
            i += 1
    
    def _detect_sensitive_endpoints(self, file_path: str, content: str):
        """Detect sensitive endpoints and check their security"""
        lines = content.split('\n')
        
        for endpoint_info in self.patterns.get('sensitive_endpoints', []):
            pattern = endpoint_info['pattern']
            severity = endpoint_info['severity']
            description = endpoint_info['description']
            
            regex = re.compile(pattern, re.IGNORECASE)
            
            for line_num, line in enumerate(lines, start=1):
                if regex.search(line):
                    finding = {
                        'id': f"FINDING-{len(self.findings) + 1:04d}",
                        'type': 'sensitive_endpoint',
                        'name': 'Sensitive Endpoint Detected',
                        'severity': severity,
                        'confidence': 0.80,
                        'file_path': file_path,
                        'line_number': line_num,
                        'line_content': line.strip(),
                        'description': description,
                        'remediation': 'Ensure proper authentication, authorization, and audit logging',
                        'evidence': {
                            'pattern': pattern,
                            'requires_auth': endpoint_info.get('requires_auth', True),
                            'requires_role': endpoint_info.get('requires_role'),
                            'requires_encryption': endpoint_info.get('requires_encryption', False)
                        }
                    }
                    
                    self.findings.append(finding)
    
    def _detect_cors_issues(self, file_path: str, content: str):
        """Detect CORS configuration issues"""
        lines = content.split('\n')
        
        for cors_info in self.patterns.get('cors_issues', []):
            pattern = cors_info['pattern']
            severity = cors_info['severity']
            description = cors_info['description']
            remediation = cors_info['remediation']
            
            regex = re.compile(pattern, re.IGNORECASE)
            
            for line_num, line in enumerate(lines, start=1):
                if regex.search(line):
                    finding = {
                        'id': f"FINDING-{len(self.findings) + 1:04d}",
                        'type': 'cors_misconfiguration',
                        'name': 'CORS Misconfiguration',
                        'severity': severity,
                        'confidence': 0.95,
                        'file_path': file_path,
                        'line_number': line_num,
                        'line_content': line.strip(),
                        'description': description,
                        'remediation': remediation,
                        'evidence': {
                            'pattern': pattern
                        }
                    }
                    
                    self.findings.append(finding)
    
    def _detect_abandoned_code(self, file_path: str, content: str):
        """Detect abandoned or unused code blocks"""
        lines = content.split('\n')
        
        # Patterns indicating abandoned code
        abandoned_patterns = [
            (r'#\s*TODO:\s*remove', 'TODO: Remove marker'),
            (r'#\s*FIXME:\s*delete', 'FIXME: Delete marker'),
            (r'#\s*UNUSED', 'Unused code marker'),
            (r'#\s*OLD\s+CODE', 'Old code marker'),
            (r'#\s*LEGACY', 'Legacy code marker'),
            (r'if\s+False:', 'Dead code (if False)'),
            (r'if\s+0:', 'Dead code (if 0)'),
        ]
        
        for line_num, line in enumerate(lines, start=1):
            for pattern, marker_name in abandoned_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    finding = {
                        'id': f"FINDING-{len(self.findings) + 1:04d}",
                        'type': 'abandoned_code',
                        'name': 'Abandoned Code Block',
                        'severity': 'low',
                        'confidence': 0.75,
                        'file_path': file_path,
                        'line_number': line_num,
                        'line_content': line.strip(),
                        'description': f'Abandoned code detected: {marker_name}',
                        'remediation': 'Remove abandoned code to reduce technical debt',
                        'evidence': {
                            'marker': marker_name,
                            'pattern': pattern
                        }
                    }
                    
                    self.findings.append(finding)
    
    def _extract_endpoint_name(self, lines: List[str], line_num: int) -> str:
        """Extract endpoint name from surrounding lines"""
        # Look ahead for route definition
        for i in range(line_num, min(len(lines), line_num + 5)):
            route_match = re.search(r'@app\.route\(["\']([^"\']+)["\']', lines[i])
            if route_match:
                return route_match.group(1)
            
            func_match = re.search(r'def\s+(\w+)\s*\(', lines[i])
            if func_match:
                return func_match.group(1)
        
        return 'unknown'
    
    def get_summary(self) -> Dict[str, Any]:
        """Get detection summary"""
        from collections import Counter
        
        type_counts = Counter(f['type'] for f in self.findings)
        severity_counts = Counter(f['severity'] for f in self.findings)
        
        return {
            'total_findings': len(self.findings),
            'by_type': dict(type_counts),
            'by_severity': dict(severity_counts),
            'deprecated_apis': sum(1 for f in self.findings if f['type'] == 'deprecated_api'),
            'missing_auth': sum(1 for f in self.findings if f['type'] == 'missing_authentication'),
            'abandoned_code': sum(1 for f in self.findings if f['type'] == 'abandoned_code')
        }

# Made with Bob
