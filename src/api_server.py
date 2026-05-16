#!/usr/bin/env python3
"""
Bob Sentinel API Server
Flask REST API for the security analysis dashboard
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, jsonify, request
from flask_cors import CORS
import yaml
from datetime import datetime
import json
from rich.console import Console

# Initialize console for pretty printing
console = Console()

# Import core modules
from database.connection import DatabaseManager
from scanners.rust_scanner_client import RustScannerClient
from correlators.incident_correlator import IncidentCorrelator
from classifiers.severity_classifier import SeverityClassifier
from classifiers.confidence_scorer import ConfidenceScorer
from correlators.attack_path_builder import AttackPathBuilder
from ai_engine.reasoning_engine import ReasoningEngine
from ai_engine.memory_manager import MemoryManager

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Load configuration
def load_config():
    """Load configuration from YAML file"""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

CONFIG = load_config()

# Initialize components
db_manager = DatabaseManager(CONFIG['database'])
rust_scanner = RustScannerClient()
correlator = IncidentCorrelator(CONFIG['analysis']['correlation'])
classifier = SeverityClassifier(CONFIG['severity'])
confidence_scorer = ConfidenceScorer()
attack_path_builder = AttackPathBuilder()
memory_manager = MemoryManager(CONFIG['ai_engine']['memory'])
reasoning_engine = ReasoningEngine(CONFIG['ai_engine'], memory_manager=memory_manager)

# In-memory storage for demo (replace with database in production)
FINDINGS_CACHE = []
INCIDENTS_CACHE = []
BOB_ANALYSIS_CACHE = {}

def run_full_pipeline():
    """Run the complete security analysis pipeline on startup"""
    console.print("\n[cyan]🔄 Running full security analysis pipeline...[/cyan]")
    
    try:
        # Clear caches
        FINDINGS_CACHE.clear()
        INCIDENTS_CACHE.clear()
        BOB_ANALYSIS_CACHE.clear()
        
        # Step 1: Scan for findings
        console.print("[cyan]  → Step 1: Scanning for security findings...[/cyan]")
        mock_repos_path = Path(__file__).parent.parent / "mock-repos"
        findings = rust_scanner.scan([str(mock_repos_path)], use_mock=True)
        FINDINGS_CACHE.extend(findings)
        console.print(f"[green]    ✓ Found {len(findings)} security findings[/green]")
        
        # Step 2: Correlate into incidents
        console.print("[cyan]  → Step 2: Correlating findings into incidents...[/cyan]")
        incidents = correlator.correlate(findings)
        console.print(f"[green]    ✓ Created {len(incidents)} incidents[/green]")
        
        # Step 3: Classify severity
        console.print("[cyan]  → Step 3: Classifying severity...[/cyan]")
        for incident in incidents:
            severity_info = classifier.classify(incident)
            incident['severity'] = severity_info['level_name']
            incident['severity_level'] = severity_info['level']
        console.print(f"[green]    ✓ Severity classified[/green]")
        
        # Step 4: Calculate confidence
        console.print("[cyan]  → Step 4: Calculating confidence scores...[/cyan]")
        for incident in incidents:
            confidence_info = confidence_scorer.calculate_confidence(incident)
            incident['confidence_score'] = confidence_info['confidence_score']
            incident['confidence_reasons'] = confidence_info['confidence_reasons']
            incident['confidence_limitations'] = confidence_info['confidence_limitations']
        console.print(f"[green]    ✓ Confidence scores calculated[/green]")
        
        # Step 5: Build attack paths
        console.print("[cyan]  → Step 5: Building attack paths...[/cyan]")
        for incident in incidents:
            attack_path = attack_path_builder.build_attack_path(incident)
            incident['attack_path'] = attack_path
        console.print(f"[green]    ✓ Attack paths built[/green]")
        
        # Step 6: Run Bob AI analysis
        console.print("[cyan]  → Step 6: Running Bob AI analysis...[/cyan]")
        enhanced_incidents = reasoning_engine.enhance_analysis(incidents)
        
        for enhanced in enhanced_incidents:
            if 'bob_analysis' in enhanced:
                BOB_ANALYSIS_CACHE[enhanced['incident_id']] = enhanced['bob_analysis']
        
        INCIDENTS_CACHE.extend(enhanced_incidents)
        console.print(f"[green]    ✓ Bob AI analysis complete ({len(BOB_ANALYSIS_CACHE)} incidents analyzed)[/green]")
        
        # Step 7: Update AI memory
        console.print("[cyan]  → Step 7: Updating AI memory...[/cyan]")
        memory_manager.learn_from_incidents(enhanced_incidents)
        console.print(f"[green]    ✓ AI memory updated[/green]")
        
        console.print(f"\n[bold green]✅ Pipeline complete![/bold green]")
        console.print(f"   • Findings: {len(FINDINGS_CACHE)}")
        console.print(f"   • Incidents: {len(INCIDENTS_CACHE)}")
        console.print(f"   • Bob Analyses: {len(BOB_ANALYSIS_CACHE)}\n")
        
    except Exception as e:
        console.print(f"[bold red]✗ Pipeline error:[/bold red] {str(e)}")
        import traceback
        traceback.print_exc()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Bob Sentinel API',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/findings', methods=['GET'])
def get_findings():
    """Get all security findings"""
    try:
        # If cache is empty, run a scan
        if not FINDINGS_CACHE:
            # Use mock data for demo
            mock_repos_path = Path(__file__).parent.parent / "mock-repos"
            findings = rust_scanner.scan([str(mock_repos_path)], use_mock=True)
            FINDINGS_CACHE.extend(findings)
        
        return jsonify(FINDINGS_CACHE)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    """Get all security incidents"""
    try:
        # If cache is empty, correlate findings into incidents
        if not INCIDENTS_CACHE:
            if not FINDINGS_CACHE:
                # Get findings first
                mock_repos_path = Path(__file__).parent.parent / "mock-repos"
                findings = rust_scanner.scan([str(mock_repos_path)], use_mock=True)
                FINDINGS_CACHE.extend(findings)
            
            # Correlate findings into incidents
            incidents = correlator.correlate(FINDINGS_CACHE)
            
            # Classify severity and calculate confidence
            for incident in incidents:
                severity_info = classifier.classify(incident)
                incident['severity'] = severity_info['level_name']
                incident['severity_level'] = severity_info['level']
                
                confidence_info = confidence_scorer.calculate_confidence(incident)
                incident['confidence_score'] = confidence_info['confidence_score']
                incident['confidence_reasons'] = confidence_info['confidence_reasons']
                incident['confidence_limitations'] = confidence_info['confidence_limitations']
                
                # Build attack path
                attack_path = attack_path_builder.build_attack_path(incident)
                incident['attack_path'] = attack_path
            
            INCIDENTS_CACHE.extend(incidents)
        
        return jsonify(INCIDENTS_CACHE)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/incidents/<incident_id>', methods=['GET'])
def get_incident(incident_id):
    """Get a specific incident by ID"""
    try:
        # Find incident in cache
        incident = next((i for i in INCIDENTS_CACHE if i.get('incident_id') == incident_id), None)
        
        if not incident:
            return jsonify({'error': 'Incident not found'}), 404
        
        return jsonify(incident)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/incidents/<incident_id>/analyze-with-bob', methods=['POST'])
def analyze_with_bob(incident_id):
    """Run Bob AI analysis on an incident"""
    try:
        # Check if analysis already exists in cache
        if incident_id in BOB_ANALYSIS_CACHE:
            return jsonify(BOB_ANALYSIS_CACHE[incident_id])
        
        # Find incident
        incident = next((i for i in INCIDENTS_CACHE if i.get('incident_id') == incident_id), None)
        
        if not incident:
            return jsonify({'error': 'Incident not found'}), 404
        
        # Run Bob AI analysis using enhance_analysis
        enhanced_incidents = reasoning_engine.enhance_analysis([incident])
        
        if enhanced_incidents and 'bob_analysis' in enhanced_incidents[0]:
            bob_output = enhanced_incidents[0]['bob_analysis']
        else:
            bob_output = {
                'error': 'Bob analysis not available',
                'incident_id': incident_id
            }
        
        # Cache the result
        BOB_ANALYSIS_CACHE[incident_id] = bob_output
        
        # Store Bob's ai_memory output back into the JSON memory store
        if bob_output.get('ai_memory'):
            try:
                ai_mem = bob_output['ai_memory'].copy()
                # Enrich with incident context before saving
                ai_mem['source_incident_id'] = incident_id
                ai_mem['source_severity'] = incident.get('severity', 'unknown')
                ai_mem['timestamp'] = datetime.utcnow().isoformat() + 'Z'
                memory_manager.add_memory(ai_mem)
                console.print(f"[green]  ✓ Stored AI memory from {incident_id} to JSON store[/green]")
            except Exception as e:
                console.print(f"[yellow]  ⚠ Failed to store AI memory: {e}[/yellow]")
        
        # Update AI memory (legacy method - may be redundant now)
        memory_manager.learn_from_incidents([incident])
        
        return jsonify(bob_output)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def run_analysis():
    """Run a new security analysis"""
    try:
        data = request.get_json()
        paths = data.get('paths', [])
        use_mock = data.get('use_mock', True)
        use_bob = data.get('use_bob', True)
        
        if not paths:
            return jsonify({'error': 'No paths provided'}), 400
        
        # Clear caches
        FINDINGS_CACHE.clear()
        INCIDENTS_CACHE.clear()
        BOB_ANALYSIS_CACHE.clear()
        
        # Step 1: Scan for findings
        findings = rust_scanner.scan(paths, use_mock=use_mock)
        FINDINGS_CACHE.extend(findings)
        
        # Step 2: Correlate into incidents
        incidents = correlator.correlate(findings)
        
        # Step 3: Classify and score
        for incident in incidents:
            severity_info = classifier.classify(incident)
            incident['severity'] = severity_info['level_name']
            incident['severity_level'] = severity_info['level']
            
            confidence_info = confidence_scorer.calculate_confidence(incident)
            incident['confidence_score'] = confidence_info['confidence_score']
            incident['confidence_reasons'] = confidence_info['confidence_reasons']
            incident['confidence_limitations'] = confidence_info['confidence_limitations']
            
            attack_path = attack_path_builder.build_attack_path(incident)
            incident['attack_path'] = attack_path
        
        INCIDENTS_CACHE.extend(incidents)
        
        # Step 4: Run Bob analysis if requested
        if use_bob and incidents:
            enhanced_incidents = reasoning_engine.enhance_analysis(incidents)
            for enhanced in enhanced_incidents:
                if 'bob_analysis' in enhanced:
                    BOB_ANALYSIS_CACHE[enhanced['incident_id']] = enhanced['bob_analysis']
        
        return jsonify({
            'status': 'success',
            'findings_count': len(findings),
            'incidents_count': len(incidents),
            'bob_analysis_count': len(BOB_ANALYSIS_CACHE)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/memory', methods=['GET'])
def get_memory():
    """Get AI memory entries"""
    try:
        entries = memory_manager.list_all()
        return jsonify(entries)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/memory/search', methods=['POST'])
def search_memory():
    """Search AI memory"""
    try:
        data = request.get_json()
        pattern = data.get('pattern', '')
        
        if not pattern:
            return jsonify({'error': 'No search pattern provided'}), 400
        
        results = memory_manager.search(pattern)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/memory/stats', methods=['GET'])
def get_memory_stats():
    """Return memory system statistics"""
    try:
        all_memories = memory_manager.list_all()
        
        # Count by incident pattern
        patterns = {}
        for m in all_memories:
            p = m.get('incident_pattern', 'unknown')
            patterns[p] = patterns.get(p, 0) + 1
        
        return jsonify({
            'total_entries': len(all_memories),
            'unique_patterns': len(patterns),
            'top_patterns': sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:5],
            'vector_memory_available': bool(reasoning_engine.vector_memory),
            'json_memory_path': str(memory_manager.storage_path)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        return jsonify({
            'findings_count': len(FINDINGS_CACHE),
            'incidents_count': len(INCIDENTS_CACHE),
            'bob_analysis_count': len(BOB_ANALYSIS_CACHE),
            'memory_entries': len(memory_manager.list_all()),
            'last_analysis': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    console.print("\n[bold cyan]🚀 Starting Bob Sentinel API Server...[/bold cyan]")
    console.print("📍 API available at: http://localhost:8000")
    console.print("📊 Health check: http://localhost:8000/api/health")
    console.print("🔍 Findings: http://localhost:8000/api/findings")
    console.print("🚨 Incidents: http://localhost:8000/api/incidents")
    
    # Run full pipeline on startup
    run_full_pipeline()
    
    console.print("\n[bold green]✨ Server ready! Press Ctrl+C to stop[/bold green]\n")
    
    app.run(host='0.0.0.0', port=8000, debug=True)

# Made with Bob