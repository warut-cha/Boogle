"""
Integration Test for IBM Bob Components
Tests the complete flow: vector memory -> Bob reasoning -> test generation -> PR draft -> incident report
"""

import json
import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai_engine.vector_memory import VectorMemory
from src.ai_engine.bob_client import BobClient
from src.ai_engine.bob_prompt_builder import BobPromptBuilder
from src.ai_engine.bob_response_parser import BobResponseParser
from src.ai_engine.reasoning_engine import ReasoningEngine
from src.remediators.test_generator import TestGenerator
from src.remediators.pr_draft_generator import PRDraftGenerator
from src.reporters.incident_reporter import IncidentReporter


def load_sample_incident():
    """Load sample incident from contracts"""
    incident_path = Path(__file__).parent.parent / 'contracts' / 'sample_incident.json'
    with open(incident_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_sample_bob_output():
    """Load sample Bob output from contracts"""
    output_path = Path(__file__).parent.parent / 'contracts' / 'sample_bob_output.json'
    with open(output_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_vector_memory():
    """Test vector memory initialization and operations"""
    print("\n=== Testing Vector Memory ===")
    
    config = {
        'enabled': True,
        'storage_path': './models/test_vector_memory',
        'collection_name': 'test_security_incidents'
    }
    
    vector_memory = VectorMemory(config)
    stats = vector_memory.get_statistics()
    
    print(f"✓ Vector memory initialized")
    print(f"  - Enabled: {stats['enabled']}")
    print(f"  - Total entries: {stats['total_entries']}")
    
    # Test adding incident
    incident = load_sample_incident()
    bob_output = load_sample_bob_output()
    memory_entry = bob_output['ai_memory']
    
    if stats['enabled']:
        vector_memory.add_incident_memory(incident, memory_entry)
        print(f"✓ Added incident to vector memory")
        
        # Test search
        similar = vector_memory.search_similar_incidents(incident, n_results=1)
        print(f"✓ Search found {len(similar)} similar incidents")
    else:
        print("⚠ Vector memory disabled (ChromaDB not available)")
    
    return vector_memory


def test_bob_client():
    """Test Bob client initialization"""
    print("\n=== Testing Bob Client ===")
    
    config = {
        'enabled': True,
        'mock_mode': True,  # Use mock mode for testing
        'model_id': 'ibm/granite-13b-chat-v2',
        'max_tokens': 2000,
        'temperature': 0.7
    }
    
    bob_client = BobClient(config)
    health = bob_client.health_check()
    
    print(f"✓ Bob client initialized")
    print(f"  - Enabled: {health['enabled']}")
    print(f"  - Mock mode: {health['mock_mode']}")
    print(f"  - Model: {health['model_id']}")
    
    # Test analysis with mock data
    incident = load_sample_incident()
    bob_input = {
        'incident': incident,
        'attack_path': incident['attack_path'],
        'confidence': {
            'score': incident['confidence_score'],
            'reasons': incident['confidence_reasons'],
            'limitations': incident['confidence_limitations']
        },
        'related_memory': [],
        'requested_outputs': [
            'attack_explanation',
            'fix_plan',
            'security_tests',
            'incident_report',
            'pr_draft'
        ]
    }
    
    bob_output = bob_client.analyze_incident(bob_input)
    
    print(f"✓ Bob analysis completed")
    print(f"  - Attack type: {bob_output.get('attack_type', 'N/A')[:50]}...")
    print(f"  - Fixes: {len(bob_output.get('recommended_fixes', []))}")
    print(f"  - Tests: {len(bob_output.get('generated_security_tests', []))}")
    
    return bob_client, bob_output


def test_prompt_builder():
    """Test prompt builder"""
    print("\n=== Testing Prompt Builder ===")
    
    incident = load_sample_incident()
    bob_input = {
        'incident': incident,
        'attack_path': incident['attack_path'],
        'confidence': {
            'score': incident['confidence_score'],
            'reasons': incident['confidence_reasons'],
            'limitations': incident['confidence_limitations']
        },
        'related_memory': [],
        'requested_outputs': ['attack_explanation', 'fix_plan']
    }
    
    prompt_builder = BobPromptBuilder()
    prompt = prompt_builder.build_prompt(bob_input)
    
    print(f"✓ Prompt built successfully")
    print(f"  - Length: {len(prompt)} characters")
    print(f"  - Contains incident: {'incident_id' in prompt.lower()}")
    print(f"  - Contains attack path: {'attack path' in prompt.lower()}")
    
    return prompt


def test_response_parser():
    """Test response parser"""
    print("\n=== Testing Response Parser ===")
    
    incident = load_sample_incident()
    bob_output_json = load_sample_bob_output()
    
    # Simulate Bob response
    response = json.dumps(bob_output_json)
    
    parser = BobResponseParser()
    bob_input = {'incident': incident}
    parsed_output = parser.parse_response(response, bob_input)
    
    print(f"✓ Response parsed successfully")
    print(f"  - Attack type: {parsed_output.get('attack_type', 'N/A')[:50]}...")
    print(f"  - Has fixes: {bool(parsed_output.get('recommended_fixes'))}")
    print(f"  - Has tests: {bool(parsed_output.get('generated_security_tests'))}")
    print(f"  - Has report: {bool(parsed_output.get('incident_report'))}")
    
    return parsed_output


def test_reasoning_engine(vector_memory):
    """Test reasoning engine"""
    print("\n=== Testing Reasoning Engine ===")
    
    config = {
        'bob': {
            'enabled': True,
            'mock_mode': True
        },
        'vector_memory': {
            'enabled': True,
            'storage_path': './models/test_vector_memory'
        },
        'local_models': {
            'enabled': True
        }
    }
    
    reasoning_engine = ReasoningEngine(config)
    
    incident = load_sample_incident()
    enhanced_incidents = reasoning_engine.enhance_analysis([incident])
    
    print(f"✓ Reasoning engine analysis completed")
    print(f"  - Incidents analyzed: {len(enhanced_incidents)}")
    
    if enhanced_incidents:
        enhanced = enhanced_incidents[0]
        print(f"  - Has Bob analysis: {bool(enhanced.get('bob_analysis'))}")
        print(f"  - Has risk assessment: {bool(enhanced.get('risk_assessment'))}")
    
    return enhanced_incidents


def test_test_generator(bob_output):
    """Test security test generator"""
    print("\n=== Testing Test Generator ===")
    
    config = {
        'output_directory': './generated_tests',
        'test_framework': 'pytest'
    }
    
    test_generator = TestGenerator(config)
    
    incident = load_sample_incident()
    test_files = test_generator.generate_tests_from_bob_output(bob_output, incident)
    
    print(f"✓ Test generation completed")
    print(f"  - Test files created: {len(test_files)}")
    
    for test_file in test_files:
        print(f"  - {test_file}")
    
    # Generate test suite
    incident['bob_analysis'] = bob_output
    test_summary = test_generator.generate_test_suite([incident])
    
    print(f"✓ Test suite generated")
    print(f"  - Total tests: {test_summary['test_count']}")
    print(f"  - Suite runner: {test_summary['suite_runner']}")
    
    # Generate README
    readme = test_generator.generate_readme(test_summary)
    print(f"✓ Test README generated: {readme}")
    
    return test_files


def test_pr_draft_generator(bob_output):
    """Test PR draft generator"""
    print("\n=== Testing PR Draft Generator ===")
    
    config = {
        'output_directory': './generated_reports',
        'template_style': 'github'
    }
    
    pr_generator = PRDraftGenerator(config)
    
    incident = load_sample_incident()
    pr_info = pr_generator.generate_pr_draft(bob_output, incident)
    
    print(f"✓ PR draft generated")
    print(f"  - Branch: {pr_info['branch_name']}")
    print(f"  - Title: {pr_info['pr_title']}")
    print(f"  - Description file: {pr_info['pr_description_file']}")
    print(f"  - Git commands: {pr_info['git_commands_file']}")
    print(f"  - Files to change: {len(pr_info['files_to_change'])}")
    
    return pr_info


def test_incident_reporter(bob_output):
    """Test incident reporter"""
    print("\n=== Testing Incident Reporter ===")
    
    config = {
        'output_directory': './generated_reports',
        'formats': ['markdown', 'json'],
        'use_bob_reports': True
    }
    
    reporter = IncidentReporter(config)
    
    incident = load_sample_incident()
    incident['bob_analysis'] = bob_output
    
    report_paths = reporter.generate_reports([incident])
    
    print(f"✓ Incident reports generated")
    print(f"  - Total reports: {len(report_paths)}")
    
    for report_path in report_paths:
        print(f"  - {report_path}")
    
    return report_paths


def run_all_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("IBM Bob Integration Tests")
    print("=" * 60)
    
    try:
        # Test 1: Vector Memory
        vector_memory = test_vector_memory()
        
        # Test 2: Bob Client
        bob_client, bob_output = test_bob_client()
        
        # Test 3: Prompt Builder
        prompt = test_prompt_builder()
        
        # Test 4: Response Parser
        parsed_output = test_response_parser()
        
        # Test 5: Reasoning Engine
        enhanced_incidents = test_reasoning_engine(vector_memory)
        
        # Test 6: Test Generator
        test_files = test_test_generator(bob_output)
        
        # Test 7: PR Draft Generator
        pr_info = test_pr_draft_generator(bob_output)
        
        # Test 8: Incident Reporter
        report_paths = test_incident_reporter(bob_output)
        
        print("\n" + "=" * 60)
        print("✓ All Integration Tests Passed!")
        print("=" * 60)
        
        print("\n📊 Summary:")
        print(f"  - Vector memory: {'✓ Working' if vector_memory else '✗ Failed'}")
        print(f"  - Bob client: ✓ Working (mock mode)")
        print(f"  - Prompt builder: ✓ Working")
        print(f"  - Response parser: ✓ Working")
        print(f"  - Reasoning engine: ✓ Working")
        print(f"  - Test generator: ✓ {len(test_files)} files created")
        print(f"  - PR draft generator: ✓ Generated")
        print(f"  - Incident reporter: ✓ {len(report_paths)} reports created")
        
        print("\n📁 Generated Files:")
        print("  - Tests: ./generated_tests/")
        print("  - Reports: ./generated_reports/")
        print("  - Vector DB: ./models/test_vector_memory/")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

# Made with Bob
