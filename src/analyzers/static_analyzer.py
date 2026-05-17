"""
Static Code Analyzer
Detects hardcoded secrets, credentials, and security vulnerabilities in source code
"""

import re
import json
import math
from pathlib import Path
from typing import List, Dict, Any, Set
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class StaticAnalyzer:
    """Analyzes source code for security vulnerabilities"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize static analyzer
        
        Args:
            config: Security configuration dictionary
        """
        self.config = config
        self.patterns = self._load_patterns()
        self.findings: List[Dict[str, Any]] = []
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load secret detection patterns from JSON file"""
        patterns_file = self.config.get('secret_patterns_file', './patterns/secret_patterns.json')
        
        try:
            with open(patterns_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load patterns: {str(e)}")
            return {'patterns': [], 'entropy_check': {'enabled': False}}
    
    def analyze(self, code_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze code for security vulnerabilities
        
        Args:
            code_data: Dictionary containing code files and metadata
            
        Returns:
            List of findings
        """
        self.findings = []
        
        files = code_data.get('files', [])
        
        for file_info in files:
            file_path = file_info['path']
            content = file_info['content']
            
            logger.info(f"Analyzing file: {file_path}")
            
            # Detect secrets using patterns
            self._detect_secrets(file_path, content)
            
            # Check for high entropy strings
            if self.patterns.get('entropy_check', {}).get('enabled', False):
                self._detect_high_entropy(file_path, content)
            
            # Detect common vulnerabilities
            self._detect_vulnerabilities(file_path, content)
        
        logger.info(f"Static analysis complete. Found {len(self.findings)} issues.")
        return self.findings
    
    def _detect_secrets(self, file_path: str, content: str):
        """Detect hardcoded secrets using regex patterns"""
        lines = content.split('\n')
        
        for pattern_info in self.patterns.get('patterns', []):
            pattern_id = pattern_info['id']
            pattern = pattern_info['pattern']
            name = pattern_info['name']
            severity = pattern_info['severity']
            confidence = pattern_info['confidence']
            description = pattern_info['description']
            remediation = pattern_info['remediation']
            
            try:
                regex = re.compile(pattern, re.MULTILINE | re.IGNORECASE)
                
                for line_num, line in enumerate(lines, start=1):
                    matches = regex.finditer(line)
                    
                    for match in matches:
                        # Check if it's in a comment (basic check)
                        if self._is_in_comment(line):
                            continue
                        
                        # Extract the matched secret
                        secret_value = match.group(0)
                        
                        # Check context for false positives
                        if self._is_likely_false_positive(line, secret_value):
                            continue
                        
                        finding = {
                            'id': f"FINDING-{len(self.findings) + 1:04d}",
                            'type': 'secret_leak',
                            'pattern_id': pattern_id,
                            'name': name,
                            'severity': severity,
                            'confidence': confidence,
                            'file_path': file_path,
                            'line_number': line_num,
                            'line_content': line.strip(),
                            'matched_value': self._mask_secret(secret_value),
                            'description': description,
                            'remediation': remediation,
                            'evidence': {
                                'pattern': pattern,
                                'match': self._mask_secret(secret_value),
                                'context': self._get_context(lines, line_num)
                            }
                        }
                        
                        self.findings.append(finding)
                        logger.warning(f"Secret detected: {name} in {file_path}:{line_num}")
            
            except re.error as e:
                logger.error(f"Invalid regex pattern '{pattern}': {str(e)}")
    
    def _detect_high_entropy(self, file_path: str, content: str):
        """Detect high-entropy strings that might be secrets"""
        entropy_config = self.patterns.get('entropy_check', {})
        threshold = entropy_config.get('threshold', 4.5)
        min_length = entropy_config.get('min_length', 16)
        
        lines = content.split('\n')
        
        # Pattern to find quoted strings
        string_pattern = re.compile(r'["\']([^"\']{' + str(min_length) + r',})["\']')
        
        for line_num, line in enumerate(lines, start=1):
            matches = string_pattern.finditer(line)
            
            for match in matches:
                string_value = match.group(1)
                entropy = self._calculate_entropy(string_value)
                
                if entropy >= threshold:
                    # Check if it's near a context keyword
                    has_context = any(
                        keyword in line.lower() 
                        for keyword in self.patterns.get('context_keywords', [])
                    )
                    
                    if has_context:
                        finding = {
                            'id': f"FINDING-{len(self.findings) + 1:04d}",
                            'type': 'high_entropy_string',
                            'name': 'High Entropy String (Possible Secret)',
                            'severity': 'medium',
                            'confidence': 0.7,
                            'file_path': file_path,
                            'line_number': line_num,
                            'line_content': line.strip(),
                            'matched_value': self._mask_secret(string_value),
                            'description': f'High entropy string detected (entropy: {entropy:.2f})',
                            'remediation': 'Review this string and move to environment variables if it is a secret',
                            'evidence': {
                                'entropy': entropy,
                                'threshold': threshold,
                                'length': len(string_value),
                                'context': self._get_context(lines, line_num)
                            }
                        }
                        
                        self.findings.append(finding)
    
    def _detect_vulnerabilities(self, file_path: str, content: str):
        """Detect common security vulnerabilities"""
        lines = content.split('\n')
        
        vulnerability_patterns = [
            {
                'id': 'sql_injection',
                'pattern': r'(?:execute|cursor\.execute|query)\s*\(\s*f["\'].*?\{.*?\}.*?["\']',
                'name': 'SQL Injection Vulnerability',
                'severity': 'high',
                'description': 'SQL query uses string formatting which is vulnerable to injection'
            },
            {
                'id': 'command_injection',
                'pattern': r'(?:os\.system|subprocess\.run|subprocess\.call)\s*\([^)]*shell\s*=\s*True',
                'name': 'Command Injection Vulnerability',
                'severity': 'critical',
                'description': 'Command execution with shell=True is vulnerable to injection'
            },
            {
                'id': 'debug_enabled',
                'pattern': r'DEBUG\s*=\s*True|debug\s*=\s*True',
                'name': 'Debug Mode Enabled',
                'severity': 'medium',
                'description': 'Debug mode should be disabled in production'
            },
            {
                'id': 'weak_crypto',
                'pattern': r'(?:MD5|SHA1)\s*\(',
                'name': 'Weak Cryptographic Algorithm',
                'severity': 'medium',
                'description': 'MD5 and SHA1 are cryptographically weak'
            },
            {
                'id': 'insecure_random',
                'pattern': r'random\.random\(\)|random\.randint\(',
                'name': 'Insecure Random Number Generation',
                'severity': 'low',
                'description': 'Use secrets module for cryptographic randomness'
            }
        ]
        
        for vuln in vulnerability_patterns:
            pattern = re.compile(vuln['pattern'], re.IGNORECASE)
            
            for line_num, line in enumerate(lines, start=1):
                if pattern.search(line):
                    finding = {
                        'id': f"FINDING-{len(self.findings) + 1:04d}",
                        'type': 'vulnerability',
                        'pattern_id': vuln['id'],
                        'name': vuln['name'],
                        'severity': vuln['severity'],
                        'confidence': 0.85,
                        'file_path': file_path,
                        'line_number': line_num,
                        'line_content': line.strip(),
                        'description': vuln['description'],
                        'remediation': self._get_vulnerability_remediation(vuln['id']),
                        'evidence': {
                            'pattern': vuln['pattern'],
                            'context': self._get_context(lines, line_num)
                        }
                    }
                    
                    self.findings.append(finding)
    
    def _calculate_entropy(self, string: str) -> float:
        """
        Calculate Shannon entropy of a string
        
        Args:
            string: Input string
            
        Returns:
            Entropy value
        """
        if not string:
            return 0.0
        
        # Count character frequencies
        char_counts = Counter(string)
        length = len(string)
        
        # Calculate entropy
        entropy = 0.0
        for count in char_counts.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _mask_secret(self, secret: str) -> str:
        """
        Mask a secret value for safe display
        
        Args:
            secret: Secret string to mask
            
        Returns:
            Masked string
        """
        if len(secret) <= 8:
            return '*' * len(secret)
        
        # Show first 4 and last 4 characters
        return f"{secret[:4]}{'*' * (len(secret) - 8)}{secret[-4:]}"
    
    def _is_in_comment(self, line: str) -> bool:
        """Check if line is a comment"""
        stripped = line.strip()
        return (
            stripped.startswith('#') or 
            stripped.startswith('//') or 
            stripped.startswith('/*') or
            stripped.startswith('*')
        )
    
    def _is_likely_false_positive(self, line: str, value: str) -> bool:
        """Check if detection is likely a false positive"""
        # Check for example/placeholder values
        false_positive_indicators = [
            'example', 'sample', 'test', 'dummy', 'placeholder',
            'your_', 'my_', 'insert_', 'replace_', 'xxx', '123'
        ]
        
        line_lower = line.lower()
        value_lower = value.lower()
        
        return any(indicator in line_lower or indicator in value_lower 
                   for indicator in false_positive_indicators)
    
    def _get_context(self, lines: List[str], line_num: int, context_size: int = 2) -> List[str]:
        """
        Get surrounding lines for context
        
        Args:
            lines: All lines in file
            line_num: Target line number (1-indexed)
            context_size: Number of lines before and after
            
        Returns:
            List of context lines
        """
        start = max(0, line_num - context_size - 1)
        end = min(len(lines), line_num + context_size)
        
        context = []
        for i in range(start, end):
            context.append(f"{i + 1}: {lines[i]}")
        
        return context
    
    def _get_vulnerability_remediation(self, vuln_id: str) -> str:
        """Get remediation advice for vulnerability"""
        remediations = {
            'sql_injection': 'Use parameterized queries or ORM instead of string formatting',
            'command_injection': 'Avoid shell=True, use list arguments, or validate input strictly',
            'debug_enabled': 'Set DEBUG=False in production environments',
            'weak_crypto': 'Use SHA-256 or stronger algorithms for cryptographic purposes',
            'insecure_random': 'Use secrets module (secrets.token_bytes, secrets.token_hex) for security'
        }
        
        return remediations.get(vuln_id, 'Review and fix this vulnerability')
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get analysis summary
        
        Returns:
            Summary statistics
        """
        severity_counts = Counter(f['severity'] for f in self.findings)
        type_counts = Counter(f['type'] for f in self.findings)
        
        return {
            'total_findings': len(self.findings),
            'by_severity': dict(severity_counts),
            'by_type': dict(type_counts),
            'files_analyzed': len(set(f['file_path'] for f in self.findings))
        }

# Made with Bob
