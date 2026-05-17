import os
import sys
import json
import subprocess
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from scanners.rust_scanner_client import RustScannerClient
from correlators.incident_correlator import IncidentCorrelator
from classifiers.severity_classifier import SeverityClassifier
from ai_engine.reasoning_engine import ReasoningEngine

def test():
    # Load the 31 findings from out.json
    with open("rust-scanner/out.json", "r") as f:
        findings_json = json.load(f)
        
    rust_scanner = RustScannerClient(rust_scanner_path="/Users/sxy/job_apply/IBM-BOB/rust-scanner")
    findings = rust_scanner._normalize_findings(findings_json)
    
    correlator = IncidentCorrelator({})
    classifier = SeverityClassifier({})
    reasoning_engine = ReasoningEngine({})
    
    FINDINGS_CACHE = []
    FINDINGS_CACHE.extend(findings)
    
    print("Running correlator...")
    incidents = correlator.correlate(FINDINGS_CACHE)
    
    print("Running classifier...")
    for incident in incidents:
        severity_info = classifier.classify(incident)
        
    print("Running reasoning engine...")
    try:
        # Mock Bob enabled locally
        reasoning_engine.bob_enabled = False
        enhanced_incidents = reasoning_engine.enhance_analysis(incidents)
        print("Reasoning Engine completed successfully.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"ERROR: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test()
