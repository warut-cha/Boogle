#!/usr/bin/env python3
"""
Test script for Bob Sentinel pipeline
Tests the complete flow from findings to incidents with attack paths
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from scanners.rust_scanner_client import RustScannerClient
from correlators.incident_correlator import IncidentCorrelator
from classifiers.severity_classifier import SeverityClassifier
from classifiers.confidence_scorer import ConfidenceScorer
from correlators.attack_path_builder import AttackPathBuilder

def test_pipeline():
    """Test the complete pipeline"""
    print("=" * 80)
    print("Bob Sentinel Pipeline Test")
    print("=" * 80)
    
    # Step 1: Get mock findings
    print("\n[1/5] Loading mock findings...")
    scanner = RustScannerClient()
    findings = scanner.scan(['./mock-repos'], use_mock=True)
    print(f"✓ Loaded {len(findings)} findings")
    
    # Display findings
    for finding in findings:
        print(f"  - {finding['finding_type']}: {finding['evidence'][:60]}...")
    
    # Step 2: Correlate into incidents
    print("\n[2/5] Correlating incidents...")
    config = {
        'time_window_minutes': 120,
        'min_confidence': 0.7,
        'correlation_types': ['temporal', 'credential', 'target', 'actor', 'attack_chain']
    }
    correlator = IncidentCorrelator(config)
    incidents = correlator.correlate(findings)
    print(f"✓ Created {len(incidents)} incidents")
    
    # Step 3: Classify severity
    print("\n[3/5] Classifying severity...")
    severity_config = {
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
    }
    classifier = SeverityClassifier(severity_config)
    
    for incident in incidents:
        severity_info = classifier.classify(incident)
        incident['severity'] = severity_info['level_name']
        incident['severity_level'] = severity_info['level']
    
    print(f"✓ Classified {len(incidents)} incidents")
    
    # Step 4: Calculate confidence
    print("\n[4/5] Calculating confidence scores...")
    confidence_scorer = ConfidenceScorer()
    
    for incident in incidents:
        confidence_info = confidence_scorer.calculate_confidence(incident)
        incident['confidence_score'] = confidence_info['confidence_score']
        incident['confidence_reasons'] = confidence_info['confidence_reasons']
        incident['confidence_limitations'] = confidence_info['confidence_limitations']
    
    print(f"✓ Calculated confidence for {len(incidents)} incidents")
    
    # Step 5: Build attack paths
    print("\n[5/5] Building attack paths...")
    attack_path_builder = AttackPathBuilder()
    
    for incident in incidents:
        attack_path = attack_path_builder.build_attack_path(incident)
        incident['attack_path'] = attack_path
    
    print(f"✓ Built attack paths for {len(incidents)} incidents")
    
    # Display results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    for i, incident in enumerate(incidents, 1):
        print(f"\n[Incident {i}] {incident.get('title', 'Unknown')}")
        print(f"  ID: {incident.get('incident_id', 'N/A')}")
        print(f"  Severity: {incident.get('severity', 'unknown')} (Level {incident.get('severity_level', 0)})")
        print(f"  Confidence: {incident.get('confidence_score', 0.0):.2f}")
        print(f"  Findings: {len(incident.get('findings', []))}")
        
        # Display confidence reasons
        if incident.get('confidence_reasons'):
            print(f"  Confidence Reasons:")
            for reason in incident['confidence_reasons'][:3]:
                print(f"    • {reason}")
        
        # Display attack path
        attack_path = incident.get('attack_path', {})
        nodes = attack_path.get('nodes', [])
        if nodes:
            print(f"  Attack Path: {len(nodes)} nodes")
            for node in nodes[:3]:
                print(f"    → {node['label']} ({node['type']})")
    
    # Save first incident to JSON for inspection
    if incidents:
        output_file = Path('test_incident_output.json')
        with open(output_file, 'w') as f:
            json.dump(incidents[0], f, indent=2)
        print(f"\n✓ Saved first incident to {output_file}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED SUCCESSFULLY")
    print("=" * 80)
    
    return incidents

if __name__ == '__main__':
    try:
        incidents = test_pipeline()
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made with Bob
