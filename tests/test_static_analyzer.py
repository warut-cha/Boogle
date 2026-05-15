"""
Unit tests for Static Analyzer
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from analyzers.static_analyzer import StaticAnalyzer


class TestStaticAnalyzer:
    """Test suite for Static Analyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        config = {
            'secret_patterns_file': './patterns/secret_patterns.json',
            'secret_detection': {
                'entropy_threshold': 4.5,
                'min_length': 16,
                'check_entropy': True
            }
        }
        return StaticAnalyzer(config)
    
    @pytest.fixture
    def sample_code_with_secrets(self):
        """Sample code containing secrets"""
        return {
            'files': [
                {
                    'path': 'test_config.py',
                    'content': '''
# Configuration file
AWS_ACCESS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE'
AWS_SECRET_ACCESS_KEY = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
DATABASE_PASSWORD = 'SuperSecret123!'
API_KEY = 'sk_live_51HqT2KLkjsdhf8234hsdfKJHSDFkjh234'
''',
                    'size': 200,
                    'line_count': 6
                }
            ]
        }
    
    def test_detect_aws_credentials(self, analyzer, sample_code_with_secrets):
        """Test AWS credential detection"""
        findings = analyzer.analyze(sample_code_with_secrets)
        
        # Should detect AWS access key and secret key
        aws_findings = [f for f in findings if 'aws' in f.get('pattern_id', '').lower()]
        assert len(aws_findings) >= 1, "Should detect AWS credentials"
        
        # Check finding structure
        for finding in aws_findings:
            assert 'id' in finding
            assert 'type' in finding
            assert 'severity' in finding
            assert 'file_path' in finding
            assert 'line_number' in finding
    
    def test_detect_stripe_key(self, analyzer, sample_code_with_secrets):
        """Test Stripe API key detection"""
        findings = analyzer.analyze(sample_code_with_secrets)
        
        stripe_findings = [f for f in findings if 'stripe' in f.get('pattern_id', '').lower()]
        assert len(stripe_findings) >= 1, "Should detect Stripe API key"
    
    def test_entropy_calculation(self, analyzer):
        """Test entropy calculation"""
        # High entropy string (random)
        high_entropy = "aB3$xY9#mK2@pL5"
        entropy_high = analyzer._calculate_entropy(high_entropy)
        
        # Low entropy string (repeated)
        low_entropy = "aaaaaaaaaa"
        entropy_low = analyzer._calculate_entropy(low_entropy)
        
        assert entropy_high > entropy_low, "Random string should have higher entropy"
        assert entropy_high > 3.0, "High entropy string should exceed threshold"
    
    def test_secret_masking(self, analyzer):
        """Test secret masking"""
        secret = "AKIAIOSFODNN7EXAMPLE"
        masked = analyzer._mask_secret(secret)
        
        assert masked != secret, "Secret should be masked"
        assert '*' in masked, "Masked secret should contain asterisks"
        assert len(masked) == len(secret), "Masked length should match original"
    
    def test_sql_injection_detection(self, analyzer):
        """Test SQL injection vulnerability detection"""
        code_with_sqli = {
            'files': [
                {
                    'path': 'database.py',
                    'content': '''
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
''',
                    'size': 100,
                    'line_count': 4
                }
            ]
        }
        
        findings = analyzer.analyze(code_with_sqli)
        sqli_findings = [f for f in findings if f.get('pattern_id') == 'sql_injection']
        
        assert len(sqli_findings) >= 1, "Should detect SQL injection vulnerability"
    
    def test_no_false_positives_in_comments(self, analyzer):
        """Test that secrets in comments are ignored"""
        code_with_comment = {
            'files': [
                {
                    'path': 'example.py',
                    'content': '''
# Example: AWS_ACCESS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE'
# This is just an example, not a real key
actual_key = os.getenv('AWS_ACCESS_KEY_ID')
''',
                    'size': 150,
                    'line_count': 4
                }
            ]
        }
        
        findings = analyzer.analyze(code_with_comment)
        # Should have fewer findings since comments are filtered
        assert len(findings) < 2, "Should filter out secrets in comments"
    
    def test_get_summary(self, analyzer, sample_code_with_secrets):
        """Test analysis summary generation"""
        findings = analyzer.analyze(sample_code_with_secrets)
        summary = analyzer.get_summary()
        
        assert 'total_findings' in summary
        assert 'by_severity' in summary
        assert 'by_type' in summary
        assert summary['total_findings'] == len(findings)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

# Made with Bob
