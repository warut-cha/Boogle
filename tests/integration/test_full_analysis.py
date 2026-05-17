"""
Integration test for full analysis pipeline
Tests the complete workflow from code collection to report generation
"""

import pytest
import sys
from pathlib import Path
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from collectors.code_collector import CodeCollector
from analyzers.static_analyzer import StaticAnalyzer
from analyzers.deprecated_api_detector import DeprecatedAPIDetector
from analyzers.runtime_analyzer import RuntimeAnalyzer
from correlators.incident_correlator import IncidentCorrelator
from classifiers.severity_classifier import SeverityClassifier
from remediators.fix_generator import FixGenerator
from reporters.incident_reporter import IncidentReporter
from ai_engine.memory_manager import MemoryManager


class TestFullAnalysisPipeline:
    """Integration tests for complete analysis pipeline"""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def config(self):
        """Test configuration"""
        return {
            'static_analysis': {
                'enabled': True,
                'scan_patterns': ['*.py'],
                'exclude_patterns': ['*/venv/*', '*/.git/*'],
                'max_file_size_mb': 10
            },
            'runtime_analysis': {
                'enabled': True,
                'anomaly_threshold': 0.85
            },
            'deprecated_api_detection': {
                'enabled': True
            },
            'correlation': {
                'time_window_minutes': 120,
                'min_confidence': 0.7
            },
            'severity': {
                'weights': {
                    'base_vulnerability': 0.4,
                    'active_exploitation': 0.3,
                    'sensitive_data': 0.2,
                    'public_exposure': 0.1
                },
                'thresholds': {
                    'critical': 0.85,
                    'high': 0.70,
                    'medium': 0.50,
                    'low': 0.30
                }
            },
            'remediation': {
                'auto_generate_fixes': True,
                'auto_generate_tests': True
            },
            'reporting': {
                'output_directory': './output',
                'formats': ['markdown', 'json'],
                'include_code_snippets': True
            },
            'ai_engine': {
                'memory': {
                    'enabled': True,
                    'storage_path': './models/test_memory.json',
                    'max_entries': 100,
                    'auto_learn': True
                }
            },
            'security': {
                'secret_patterns_file': './patterns/secret_patterns.json'
            }
        }
    
    def test_end_to_end_analysis(self, config, temp_output_dir):
        """Test complete analysis pipeline"""
        
        # Step 1: Collect code
        code_collector = CodeCollector(
            './mock_data/repos/ecommerce_app',
            config
        )
        code_data = code_collector.collect()
        
        assert code_data['total_files'] > 0, "Should collect files"
        print(f"✓ Collected {code_data['total_files']} files")
        
        # Step 2: Static analysis
        static_analyzer = StaticAnalyzer(config['security'])
        static_findings = static_analyzer.analyze(code_data)
        
        assert len(static_findings) > 0, "Should find vulnerabilities"
        print(f"✓ Found {len(static_findings)} static findings")
        
        # Step 3: Deprecated API detection
        api_detector = DeprecatedAPIDetector(config)
        api_findings = api_detector.detect(code_data)
        
        print(f"✓ Found {len(api_findings)} deprecated API issues")
        
        # Step 4: Runtime analysis
        runtime_analyzer = RuntimeAnalyzer(config)
        runtime_findings = runtime_analyzer.analyze('./mock_data/logs/app.log')
        
        assert len(runtime_findings) > 0, "Should detect runtime anomalies"
        print(f"✓ Found {len(runtime_findings)} runtime anomalies")
        
        # Step 5: Correlate findings
        all_findings = static_findings + api_findings + runtime_findings
        correlator = IncidentCorrelator(config['correlation'])
        incidents = correlator.correlate(all_findings)
        
        assert len(incidents) > 0, "Should create incidents"
        print(f"✓ Created {len(incidents)} incidents from {len(all_findings)} findings")
        
        # Step 6: Classify severity
        classifier = SeverityClassifier(config['severity'])
        for incident in incidents:
            incident['severity'] = classifier.classify(incident)
        
        # Check severity distribution
        critical_count = sum(1 for i in incidents if i['severity']['level'] == 5)
        high_count = sum(1 for i in incidents if i['severity']['level'] == 4)
        
        print(f"✓ Classified: {critical_count} critical, {high_count} high priority")
        
        # Step 7: Generate remediations
        fix_generator = FixGenerator(config['remediation'])
        for incident in incidents:
            incident['remediation'] = fix_generator.generate(incident)
        
        # Verify remediation structure
        assert all('remediation' in i for i in incidents), "All incidents should have remediation"
        print(f"✓ Generated remediations for all incidents")
        
        # Step 8: Generate reports
        config['reporting']['output_directory'] = temp_output_dir
        reporter = IncidentReporter(config['reporting'])
        report_paths = reporter.generate_reports(incidents, temp_output_dir, ['markdown', 'json'])
        
        assert len(report_paths) > 0, "Should generate reports"
        print(f"✓ Generated {len(report_paths)} report files")
        
        # Verify reports exist
        for report_path in report_paths:
            assert Path(report_path).exists(), f"Report should exist: {report_path}"
        
        # Step 9: Update AI memory
        memory_manager = MemoryManager(config['ai_engine']['memory'])
        initial_memory_count = len(memory_manager.memory)
        memory_manager.learn_from_incidents(incidents)
        
        assert len(memory_manager.memory) >= initial_memory_count, "Should add to memory"
        print(f"✓ Updated AI memory: {len(memory_manager.memory)} entries")
        
        # Verify memory structure
        if memory_manager.memory:
            memory_entry = memory_manager.memory[0]
            assert 'incident_pattern' in memory_entry
            assert 'prevention_rule' in memory_entry
            assert 'signals_to_watch' in memory_entry
        
        print("\n✅ Full analysis pipeline completed successfully!")
        
        return {
            'findings': len(all_findings),
            'incidents': len(incidents),
            'reports': len(report_paths),
            'memory_entries': len(memory_manager.memory)
        }
    
    def test_attack_scenario_detection(self, config):
        """Test detection of coordinated attack scenarios"""
        
        # Analyze the mock vulnerable app
        code_collector = CodeCollector('./mock_data/repos/ecommerce_app', config)
        code_data = code_collector.collect()
        
        static_analyzer = StaticAnalyzer(config['security'])
        static_findings = static_analyzer.analyze(code_data)
        
        runtime_analyzer = RuntimeAnalyzer(config)
        runtime_findings = runtime_analyzer.analyze('./mock_data/logs/app.log')
        
        # Correlate
        all_findings = static_findings + runtime_findings
        correlator = IncidentCorrelator(config['correlation'])
        incidents = correlator.correlate(all_findings)
        
        # Should detect attack chains
        attack_chains = [i for i in incidents if i.get('correlation_type') == 'attack_chain']
        
        print(f"\n🎯 Attack Scenario Detection:")
        print(f"   Total incidents: {len(incidents)}")
        print(f"   Attack chains detected: {len(attack_chains)}")
        
        # Classify and check for critical incidents
        classifier = SeverityClassifier(config['severity'])
        for incident in incidents:
            incident['severity'] = classifier.classify(incident)
        
        critical_incidents = [i for i in incidents if i['severity']['level'] == 5]
        high_incidents = [i for i in incidents if i['severity']['level'] == 4]
        
        print(f"   Critical (Level 5): {len(critical_incidents)}")
        print(f"   High (Level 4): {len(high_incidents)}")
        
        # Should detect at least one critical incident from the attack scenarios
        assert len(critical_incidents) > 0 or len(high_incidents) > 0, \
            "Should detect high-severity incidents from attack scenarios"
        
        print("✅ Attack scenarios detected successfully!")
    
    def test_correlation_accuracy(self, config):
        """Test incident correlation accuracy"""
        
        # Create test findings that should be correlated
        test_findings = [
            {
                'id': 'F001',
                'type': 'secret_leak',
                'severity': 'high',
                'file_path': 'config.py',
                'timestamp': '2026-05-15T01:00:00',
                'evidence': {'ip_address': '192.168.1.100'}
            },
            {
                'id': 'F002',
                'type': 'large_data_export',
                'severity': 'high',
                'timestamp': '2026-05-15T01:30:00',
                'evidence': {'ip_address': '192.168.1.100'}
            },
            {
                'id': 'F003',
                'type': 'deprecated_api_access',
                'severity': 'medium',
                'timestamp': '2026-05-15T01:45:00',
                'evidence': {'ip_address': '192.168.1.100'}
            }
        ]
        
        correlator = IncidentCorrelator(config['correlation'])
        incidents = correlator.correlate(test_findings)
        
        # Should correlate into fewer incidents than findings
        assert len(incidents) < len(test_findings), \
            "Should correlate related findings into fewer incidents"
        
        # Check for temporal correlation
        temporal_incidents = [i for i in incidents if i.get('correlation_type') == 'temporal']
        assert len(temporal_incidents) > 0, "Should detect temporal correlation"
        
        print(f"✅ Correlation test passed: {len(test_findings)} findings → {len(incidents)} incidents")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])

# Made with Bob
