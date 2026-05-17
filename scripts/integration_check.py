#!/usr/bin/env python3
"""
Integration Check Script
Verifies that all components of Jeff are properly integrated
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import List, Tuple
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text: str):
    """Print a section header"""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text: str):
    """Print error message"""
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{YELLOW}⚠ {text}{RESET}")

def check_file_exists(file_path: Path, description: str) -> bool:
    """Check if a file exists"""
    if file_path.exists():
        print_success(f"{description}: {file_path}")
        return True
    else:
        print_error(f"{description} not found: {file_path}")
        return False

def check_json_valid(file_path: Path, description: str) -> bool:
    """Check if a JSON file is valid"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            print_success(f"{description} is valid JSON (array with {len(data)} items)")
        elif isinstance(data, dict):
            print_success(f"{description} is valid JSON (object with {len(data)} keys)")
        else:
            print_success(f"{description} is valid JSON")
        return True
    except json.JSONDecodeError as e:
        print_error(f"{description} has invalid JSON: {e}")
        return False
    except Exception as e:
        print_error(f"Error reading {description}: {e}")
        return False

def run_command(cmd: List[str], cwd: Path | None = None, description: str = "") -> Tuple[bool, str]:
    """Run a command and return success status and output"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print_success(f"{description} succeeded")
            return True, result.stdout
        else:
            print_error(f"{description} failed with exit code {result.returncode}")
            if result.stderr:
                print(f"  Error: {result.stderr[:200]}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print_error(f"{description} timed out")
        return False, "Timeout"
    except Exception as e:
        print_error(f"{description} error: {e}")
        return False, str(e)

def main():
    """Run integration checks"""
    print_header("Jeff Integration Check")
    
    project_root = Path(__file__).parent.parent
    all_checks_passed = True
    
    # Check 1: Rust Scanner
    print_header("1. Rust Scanner")
    
    rust_dir = project_root / "rust-scanner"
    cargo_toml = rust_dir / "Cargo.toml"
    
    if check_file_exists(cargo_toml, "Cargo.toml"):
        success, _ = run_command(
            ["cargo", "check"],
            cwd=rust_dir,
            description="Rust scanner build check"
        )
        all_checks_passed = all_checks_passed and success
    else:
        all_checks_passed = False
    
    # Check 2: Contracts
    print_header("2. Contract Files")
    
    contracts_dir = project_root / "contracts"
    contract_files = [
        ("sample_findings.json", "Sample findings"),
        ("sample_incident.json", "Sample incident"),
        ("sample_bob_output.json", "Sample Bob output"),
        ("finding.schema.json", "Finding schema"),
        ("incident.schema.json", "Incident schema"),
        ("bob_input.schema.json", "Bob input schema"),
        ("bob_output.schema.json", "Bob output schema"),
    ]
    
    for filename, description in contract_files:
        file_path = contracts_dir / filename
        if check_file_exists(file_path, description):
            if filename.endswith('.json'):
                success = check_json_valid(file_path, description)
                all_checks_passed = all_checks_passed and success
        else:
            all_checks_passed = False
    
    # Check 3: Python Backend
    print_header("3. Python Backend")
    
    python_files = [
        ("src/main.py", "Main entry point"),
        ("src/scanners/rust_scanner_client.py", "Rust scanner client"),
        ("src/correlators/incident_correlator.py", "Incident correlator"),
        ("src/correlators/attack_path_builder.py", "Attack path builder"),
        ("src/classifiers/confidence_scorer.py", "Confidence scorer"),
        ("src/ai_engine/reasoning_engine.py", "Reasoning engine"),
        ("src/ai_engine/memory_manager.py", "Memory manager"),
        ("src/remediators/test_generator.py", "Test generator"),
        ("src/remediators/pr_draft_generator.py", "PR draft generator"),
        ("src/utils/normalizers.py", "Data normalizers"),
    ]
    
    for filename, description in python_files:
        file_path = project_root / filename
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    # Check 4: Frontend
    print_header("4. Frontend")
    
    frontend_dir = project_root / "frontend"
    package_json = frontend_dir / "package.json"
    
    if check_file_exists(package_json, "package.json"):
        success = check_json_valid(package_json, "package.json")
        all_checks_passed = all_checks_passed and success
        
        # Check TypeScript types
        types_file = frontend_dir / "src" / "api" / "types.ts"
        if check_file_exists(types_file, "TypeScript types"):
            print_success("Frontend types file exists")
        else:
            all_checks_passed = False
        
        # Check if npm is available
        print("\nChecking if npm is available...")
        npm_check, _ = run_command(
            ["npm", "--version"],
            cwd=frontend_dir,
            description="npm version check"
        )
        
        if npm_check:
            # Try to build frontend
            print("\nAttempting frontend build...")
            success, _ = run_command(
                ["npm", "run", "build"],
                cwd=frontend_dir,
                description="Frontend build"
            )
            all_checks_passed = all_checks_passed and success
        else:
            print_warning("npm not available in PATH, skipping frontend build")
    else:
        all_checks_passed = False
    
    # Check 5: Integration Flow
    print_header("5. Integration Flow Verification")
    
    print("Checking data flow compatibility:")
    
    # Load sample data and verify structure
    sample_findings_path = contracts_dir / "sample_findings.json"
    sample_incident_path = contracts_dir / "sample_incident.json"
    sample_bob_path = contracts_dir / "sample_bob_output.json"
    
    try:
        with open(sample_findings_path, 'r', encoding='utf-8') as f:
            findings = json.load(f)
        
        # Check finding structure
        if findings and len(findings) > 0:
            required_fields = ['finding_id', 'finding_type', 'severity_hint', 'source']
            finding = findings[0]
            missing_fields = [f for f in required_fields if f not in finding]
            
            if not missing_fields:
                print_success(f"Finding structure valid ({len(findings)} findings)")
            else:
                print_error(f"Finding missing fields: {missing_fields}")
                all_checks_passed = False
        
        with open(sample_incident_path, 'r', encoding='utf-8') as f:
            incident = json.load(f)
        
        # Check incident structure
        required_fields = ['incident_id', 'severity', 'confidence_score', 'attack_path', 'related_memory']
        missing_fields = [f for f in required_fields if f not in incident]
        
        if not missing_fields:
            print_success("Incident structure valid")
        else:
            print_error(f"Incident missing fields: {missing_fields}")
            all_checks_passed = False
        
        with open(sample_bob_path, 'r', encoding='utf-8') as f:
            bob_output = json.load(f)
        
        # Check Bob output structure
        required_fields = ['attack_type', 'recommended_fixes', 'generated_security_tests', 'pr_draft']
        missing_fields = [f for f in required_fields if f not in bob_output]
        
        if not missing_fields:
            print_success("Bob output structure valid")
        else:
            print_error(f"Bob output missing fields: {missing_fields}")
            all_checks_passed = False
        
    except Exception as e:
        print_error(f"Error validating data structures: {e}")
        all_checks_passed = False
    
    # Final Summary
    print_header("Integration Check Summary")
    
    if all_checks_passed:
        print_success("All integration checks passed! ✓")
        print("\nThe system is ready for end-to-end testing.")
        print("\nNext steps:")
        print("  1. Run: python src/main.py analyze --path ./mock-repos --use-mock --use-bob")
        print("  2. Check generated_tests/ for security tests")
        print("  3. Check generated_reports/ for PR drafts")
        print("  4. Run: cd frontend && npm run dev")
        return 0
    else:
        print_error("Some integration checks failed.")
        print("\nPlease fix the issues above before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
