"""
Runtime Analyzer
Analyzes logs and runtime behavior for suspicious patterns and anomalies
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)


class RuntimeAnalyzer:
    """Analyzes runtime behavior and logs for security threats"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize runtime analyzer
        
        Args:
            config: Analysis configuration
        """
        self.config = config
        self.runtime_config = config.get('runtime_analysis', {})
        self.anomaly_threshold = self.runtime_config.get('anomaly_threshold', 0.85)
        self.findings: List[Dict[str, Any]] = []
        self.log_entries: List[Dict[str, Any]] = []
    
    def analyze(self, log_path: str = './mock_data/logs/app.log') -> List[Dict[str, Any]]:
        """
        Analyze runtime behavior from logs
        
        Args:
            log_path: Path to log file
            
        Returns:
            List of findings
        """
        self.findings = []
        
        # Parse log file
        self.log_entries = self._parse_logs(log_path)
        
        logger.info(f"Analyzing {len(self.log_entries)} log entries")
        
        # Detect various attack patterns
        self._detect_rapid_requests()
        self._detect_failed_auth_attempts()
        self._detect_sql_injection_attempts()
        self._detect_large_data_exports()
        self._detect_suspicious_api_access()
        self._detect_privilege_escalation()
        self._detect_command_injection()
        self._detect_path_traversal()
        self._detect_sensitive_data_exposure()
        
        logger.info(f"Runtime analysis complete. Found {len(self.findings)} issues.")
        return self.findings
    
    def _parse_logs(self, log_path: str) -> List[Dict[str, Any]]:
        """Parse log file into structured entries"""
        entries = []
        
        try:
            with open(log_path, 'r') as f:
                for line_num, line in enumerate(f, start=1):
                    if line.strip() and not line.startswith('#'):
                        entry = self._parse_log_line(line, line_num)
                        if entry:
                            entries.append(entry)
        except FileNotFoundError:
            logger.warning(f"Log file not found: {log_path}")
        except Exception as e:
            logger.error(f"Error parsing logs: {str(e)}")
        
        return entries
    
    def _parse_log_line(self, line: str, line_num: int) -> Dict[str, Any]:
        """Parse a single log line"""
        # Pattern: YYYY-MM-DD HH:MM:SS LEVEL [component] message
        pattern = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(\w+)\s+\[(\w+)\]\s+(.+)'
        match = re.match(pattern, line)
        
        if match:
            timestamp_str, level, component, message = match.groups()
            
            # Parse timestamp
            try:
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            except:
                timestamp = None
            
            # Extract IP address if present
            ip_match = re.search(r'IP:\s*(\d+\.\d+\.\d+\.\d+)', message)
            ip_address = ip_match.group(1) if ip_match else None
            
            return {
                'line_num': line_num,
                'timestamp': timestamp,
                'level': level,
                'component': component,
                'message': message,
                'ip_address': ip_address,
                'raw': line.strip()
            }
        
        return None
    
    def _detect_rapid_requests(self):
        """Detect rapid sequential requests from same IP"""
        ip_requests = defaultdict(list)
        
        for entry in self.log_entries:
            if entry['ip_address'] and entry['timestamp']:
                ip_requests[entry['ip_address']].append(entry)
        
        for ip, requests in ip_requests.items():
            if len(requests) < 5:
                continue
            
            # Sort by timestamp
            requests.sort(key=lambda x: x['timestamp'])
            
            # Check for rapid requests (5+ requests within 10 seconds)
            for i in range(len(requests) - 4):
                window = requests[i:i+5]
                time_diff = (window[-1]['timestamp'] - window[0]['timestamp']).total_seconds()
                
                if time_diff <= 10:
                    finding = {
                        'id': f"FINDING-{len(self.findings) + 1:04d}",
                        'type': 'rapid_requests',
                        'name': 'Rapid Sequential Requests',
                        'severity': 'medium',
                        'confidence': 0.85,
                        'description': f'Detected {len(window)} requests in {time_diff:.1f} seconds from {ip}',
                        'remediation': 'Implement rate limiting and monitor for automated attacks',
                        'evidence': {
                            'ip_address': ip,
                            'request_count': len(window),
                            'time_window_seconds': time_diff,
                            'timestamps': [r['timestamp'].isoformat() for r in window]
                        }
                    }
                    
                    self.findings.append(finding)
                    break
    
    def _detect_failed_auth_attempts(self):
        """Detect brute force authentication attempts"""
        ip_auth_attempts = defaultdict(list)
        
        for entry in self.log_entries:
            if 'login' in entry['message'].lower() or 'auth' in entry['message'].lower():
                if entry['ip_address']:
                    ip_auth_attempts[entry['ip_address']].append(entry)
        
        for ip, attempts in ip_auth_attempts.items():
            failed = [a for a in attempts if 'fail' in a['message'].lower() or 'unauthorized' in a['message'].lower()]
            
            if len(failed) >= 3:
                # Check if eventually succeeded
                succeeded = [a for a in attempts if 'success' in a['message'].lower()]
                
                if succeeded:
                    finding = {
                        'id': f"FINDING-{len(self.findings) + 1:04d}",
                        'type': 'brute_force_attack',
                        'name': 'Brute Force Authentication Attack',
                        'severity': 'high',
                        'confidence': 0.90,
                        'description': f'Detected {len(failed)} failed login attempts followed by success from {ip}',
                        'remediation': 'Implement account lockout, CAPTCHA, and alert on suspicious patterns',
                        'evidence': {
                            'ip_address': ip,
                            'failed_attempts': len(failed),
                            'eventually_succeeded': True,
                            'timeline': [a['timestamp'].isoformat() for a in attempts if a['timestamp']]
                        }
                    }
                    
                    self.findings.append(finding)
    
    def _detect_sql_injection_attempts(self):
        """Detect SQL injection patterns in logs"""
        sql_patterns = [
            r"(?i)union\s+select",
            r"(?i)or\s+['\"]?1['\"]?\s*=\s*['\"]?1",
            r"(?i);\s*drop\s+table",
            r"(?i)--\s*$",
            r"(?i)'\s+or\s+'",
        ]
        
        for entry in self.log_entries:
            message = entry['message']
            
            for pattern in sql_patterns:
                if re.search(pattern, message):
                    finding = {
                        'id': f"FINDING-{len(self.findings) + 1:04d}",
                        'type': 'sql_injection_attempt',
                        'name': 'SQL Injection Attempt',
                        'severity': 'high',
                        'confidence': 0.85,
                        'description': 'SQL injection pattern detected in request',
                        'remediation': 'Use parameterized queries and input validation',
                        'evidence': {
                            'log_line': entry['line_num'],
                            'timestamp': entry['timestamp'].isoformat() if entry['timestamp'] else None,
                            'ip_address': entry['ip_address'],
                            'pattern_matched': pattern,
                            'message': message
                        }
                    }
                    
                    self.findings.append(finding)
                    break
    
    def _detect_large_data_exports(self):
        """Detect large data exports that might indicate data exfiltration"""
        export_keywords = ['export', 'download', 'backup', 'dump']
        
        for entry in self.log_entries:
            message_lower = entry['message'].lower()
            
            if any(keyword in message_lower for keyword in export_keywords):
                # Look for record counts
                count_match = re.search(r'(\d+)\s+records?', message_lower)
                if count_match:
                    count = int(count_match.group(1))
                    
                    if count >= 10000:  # Large export threshold
                        finding = {
                            'id': f"FINDING-{len(self.findings) + 1:04d}",
                            'type': 'large_data_export',
                            'name': 'Large Data Export',
                            'severity': 'high',
                            'confidence': 0.80,
                            'description': f'Large data export detected: {count} records',
                            'remediation': 'Review export permissions and implement audit logging',
                            'evidence': {
                                'log_line': entry['line_num'],
                                'timestamp': entry['timestamp'].isoformat() if entry['timestamp'] else None,
                                'ip_address': entry['ip_address'],
                                'record_count': count,
                                'message': entry['message']
                            }
                        }
                        
                        self.findings.append(finding)
    
    def _detect_suspicious_api_access(self):
        """Detect access to deprecated or sensitive APIs"""
        deprecated_apis = ['/api/v1/', '/api/v2/']
        
        for entry in self.log_entries:
            message = entry['message']
            
            # Check for deprecated API access
            for api_version in deprecated_apis:
                if api_version in message:
                    finding = {
                        'id': f"FINDING-{len(self.findings) + 1:04d}",
                        'type': 'deprecated_api_access',
                        'name': 'Deprecated API Access',
                        'severity': 'medium',
                        'confidence': 0.90,
                        'description': f'Access to deprecated API endpoint: {api_version}',
                        'remediation': 'Migrate to current API version and deprecate old endpoints',
                        'evidence': {
                            'log_line': entry['line_num'],
                            'timestamp': entry['timestamp'].isoformat() if entry['timestamp'] else None,
                            'ip_address': entry['ip_address'],
                            'api_version': api_version,
                            'message': message
                        }
                    }
                    
                    self.findings.append(finding)
                    break
    
    def _detect_privilege_escalation(self):
        """Detect privilege escalation attempts"""
        for i, entry in enumerate(self.log_entries):
            if 'role updated' in entry['message'].lower() or 'elevated' in entry['message'].lower():
                # Check if this was preceded by suspicious activity
                recent_entries = self.log_entries[max(0, i-10):i]
                
                has_suspicious_activity = any(
                    'unauthorized' in e['message'].lower() or
                    'deprecated' in e['message'].lower() or
                    'admin' in e['message'].lower()
                    for e in recent_entries
                )
                
                if has_suspicious_activity:
                    finding = {
                        'id': f"FINDING-{len(self.findings) + 1:04d}",
                        'type': 'privilege_escalation',
                        'name': 'Privilege Escalation',
                        'severity': 'critical',
                        'confidence': 0.85,
                        'description': 'User privilege elevation following suspicious activity',
                        'remediation': 'Review authorization mechanisms and implement proper access controls',
                        'evidence': {
                            'log_line': entry['line_num'],
                            'timestamp': entry['timestamp'].isoformat() if entry['timestamp'] else None,
                            'ip_address': entry['ip_address'],
                            'message': entry['message'],
                            'preceding_suspicious_activity': True
                        }
                    }
                    
                    self.findings.append(finding)
    
    def _detect_command_injection(self):
        """Detect command injection attempts"""
        for entry in self.log_entries:
            if 'command executed' in entry['message'].lower():
                # Check for suspicious commands
                suspicious_commands = ['cat /etc/passwd', 'wget', 'curl', 'nc ', 'bash', 'sh ']
                
                if any(cmd in entry['message'].lower() for cmd in suspicious_commands):
                    finding = {
                        'id': f"FINDING-{len(self.findings) + 1:04d}",
                        'type': 'command_injection',
                        'name': 'Command Injection',
                        'severity': 'critical',
                        'confidence': 0.90,
                        'description': 'Suspicious command execution detected',
                        'remediation': 'Disable command execution endpoints and validate all inputs',
                        'evidence': {
                            'log_line': entry['line_num'],
                            'timestamp': entry['timestamp'].isoformat() if entry['timestamp'] else None,
                            'ip_address': entry['ip_address'],
                            'message': entry['message']
                        }
                    }
                    
                    self.findings.append(finding)
    
    def _detect_path_traversal(self):
        """Detect path traversal attempts"""
        path_traversal_patterns = [r'\.\./\.\./\.\./etc/passwd', r'\.\./']
        
        for entry in self.log_entries:
            for pattern in path_traversal_patterns:
                if re.search(pattern, entry['message']):
                    finding = {
                        'id': f"FINDING-{len(self.findings) + 1:04d}",
                        'type': 'path_traversal',
                        'name': 'Path Traversal Attempt',
                        'severity': 'high',
                        'confidence': 0.85,
                        'description': 'Path traversal pattern detected in request',
                        'remediation': 'Implement strict path validation and sanitization',
                        'evidence': {
                            'log_line': entry['line_num'],
                            'timestamp': entry['timestamp'].isoformat() if entry['timestamp'] else None,
                            'ip_address': entry['ip_address'],
                            'pattern': pattern,
                            'message': entry['message']
                        }
                    }
                    
                    self.findings.append(finding)
                    break
    
    def _detect_sensitive_data_exposure(self):
        """Detect sensitive data in logs"""
        sensitive_patterns = [
            (r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}', 'Credit Card Number'),
            (r'password["\']?\s*:\s*["\']([^"\']+)["\']', 'Password'),
            (r'cvv["\']?\s*:\s*["\']?(\d{3,4})["\']?', 'CVV'),
        ]
        
        for entry in self.log_entries:
            for pattern, data_type in sensitive_patterns:
                if re.search(pattern, entry['message'], re.IGNORECASE):
                    finding = {
                        'id': f"FINDING-{len(self.findings) + 1:04d}",
                        'type': 'sensitive_data_in_logs',
                        'name': 'Sensitive Data Exposure in Logs',
                        'severity': 'high',
                        'confidence': 0.80,
                        'description': f'{data_type} detected in log output',
                        'remediation': 'Implement log sanitization and never log sensitive data',
                        'evidence': {
                            'log_line': entry['line_num'],
                            'timestamp': entry['timestamp'].isoformat() if entry['timestamp'] else None,
                            'data_type': data_type,
                            'message': '[REDACTED FOR SECURITY]'
                        }
                    }
                    
                    self.findings.append(finding)
                    break
    
    def get_summary(self) -> Dict[str, Any]:
        """Get analysis summary"""
        type_counts = Counter(f['type'] for f in self.findings)
        severity_counts = Counter(f['severity'] for f in self.findings)
        
        return {
            'total_findings': len(self.findings),
            'log_entries_analyzed': len(self.log_entries),
            'by_type': dict(type_counts),
            'by_severity': dict(severity_counts)
        }

# Made with Bob
