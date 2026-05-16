#!/usr/bin/env python3
"""
Test script for Bob Sentinel Real-time System
Verifies backend API, SSE events, and integration
"""

import requests
import json
import time
import sys
from threading import Thread
from queue import Queue
import sseclient

API_BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(name, passed, message=""):
    """Print test result"""
    status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
    print(f"{status} - {name}")
    if message:
        print(f"      {message}")

def test_backend_health():
    """Test 1: Backend health check"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        passed = response.status_code == 200
        data = response.json() if passed else {}
        message = f"Status: {data.get('status', 'unknown')}" if passed else f"Status code: {response.status_code}"
        print_test("Backend Health Check", passed, message)
        return passed
    except requests.exceptions.ConnectionError:
        print_test("Backend Health Check", False, "Backend not running. Start with: python src/api_server.py")
        return False
    except Exception as e:
        print_test("Backend Health Check", False, str(e))
        return False

def test_rest_endpoints():
    """Test 2: REST API endpoints"""
    endpoints = [
        ("GET", "/api/findings", "Get findings"),
        ("GET", "/api/incidents", "Get incidents"),
    ]
    
    all_passed = True
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{API_BASE_URL}{endpoint}", timeout=5)
            
            passed = response.status_code in [200, 201]
            print_test(f"REST API - {description}", passed, f"{method} {endpoint}")
            all_passed = all_passed and passed
        except Exception as e:
            print_test(f"REST API - {description}", False, str(e))
            all_passed = False
    
    return all_passed

def test_sse_connection():
    """Test 3: SSE connection"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/events", stream=True, timeout=10)
        
        if response.status_code != 200:
            print_test("SSE Connection", False, f"Status code: {response.status_code}")
            return False
        
        # Try to read first event (should be 'connected')
        client = sseclient.SSEClient(response)
        
        for i, event in enumerate(client.events()):
            if i == 0:
                data = json.loads(event.data)
                passed = data.get('type') == 'connected'
                message = f"Received: {data.get('type')}" if passed else f"Expected 'connected', got: {data.get('type')}"
                print_test("SSE Connection", passed, message)
                return passed
            break
        
        print_test("SSE Connection", False, "No events received")
        return False
        
    except Exception as e:
        print_test("SSE Connection", False, str(e))
        return False

def test_simulate_attack():
    """Test 4: Simulate attack endpoint"""
    try:
        # Clear data first
        requests.post(f"{API_BASE_URL}/api/clear", timeout=5)
        time.sleep(0.5)
        
        # Trigger simulation
        response = requests.post(f"{API_BASE_URL}/api/demo/simulate-attack", timeout=5)
        passed = response.status_code == 200
        
        if passed:
            data = response.json()
            message = data.get('message', 'Simulation started')
        else:
            message = f"Status code: {response.status_code}"
        
        print_test("Simulate Attack", passed, message)
        return passed
    except Exception as e:
        print_test("Simulate Attack", False, str(e))
        return False

def test_realtime_events():
    """Test 5: Real-time event reception"""
    try:
        print(f"\n{Colors.BLUE}Testing real-time events (this takes ~10 seconds)...{Colors.RESET}")
        
        # Clear data
        requests.post(f"{API_BASE_URL}/api/clear", timeout=5)
        time.sleep(0.5)
        
        # Connect to SSE
        response = requests.get(f"{API_BASE_URL}/api/events", stream=True, timeout=15)
        client = sseclient.SSEClient(response)
        
        # Trigger simulation in background
        def trigger_simulation():
            time.sleep(1)
            requests.post(f"{API_BASE_URL}/api/demo/simulate-attack", timeout=5)
        
        Thread(target=trigger_simulation, daemon=True).start()
        
        # Collect events
        events_received = []
        start_time = time.time()
        
        for event in client.events():
            if time.time() - start_time > 12:  # 12 second timeout
                break
            
            data = json.loads(event.data)
            event_type = data.get('type')
            events_received.append(event_type)
            
            print(f"      Received: {Colors.YELLOW}{event_type}{Colors.RESET}")
            
            # Stop after demo_complete
            if event_type == 'demo_complete':
                break
        
        # Check if we received expected events
        expected_events = ['finding_added', 'incident_added', 'demo_complete']
        passed = all(evt in events_received for evt in expected_events)
        
        if passed:
            message = f"Received {len(events_received)} events including all expected types"
        else:
            missing = [evt for evt in expected_events if evt not in events_received]
            message = f"Missing events: {missing}"
        
        print_test("Real-time Events", passed, message)
        return passed
        
    except Exception as e:
        print_test("Real-time Events", False, str(e))
        return False

def test_data_persistence():
    """Test 6: Data persistence after simulation"""
    try:
        # Wait a bit for simulation to complete
        time.sleep(1)
        
        # Check findings
        findings_response = requests.get(f"{API_BASE_URL}/api/findings", timeout=5)
        findings = findings_response.json()
        
        # Check incidents
        incidents_response = requests.get(f"{API_BASE_URL}/api/incidents", timeout=5)
        incidents = incidents_response.json()
        
        passed = len(findings) > 0 and len(incidents) > 0
        message = f"Findings: {len(findings)}, Incidents: {len(incidents)}"
        
        print_test("Data Persistence", passed, message)
        return passed
    except Exception as e:
        print_test("Data Persistence", False, str(e))
        return False

def test_clear_data():
    """Test 7: Clear data endpoint"""
    try:
        # Clear data
        response = requests.post(f"{API_BASE_URL}/api/clear", timeout=5)
        passed = response.status_code == 200
        
        if passed:
            # Verify data is cleared
            findings_response = requests.get(f"{API_BASE_URL}/api/findings", timeout=5)
            findings = findings_response.json()
            
            incidents_response = requests.get(f"{API_BASE_URL}/api/incidents", timeout=5)
            incidents = incidents_response.json()
            
            passed = len(findings) == 0 and len(incidents) == 0
            message = "Data cleared successfully" if passed else "Data not cleared"
        else:
            message = f"Status code: {response.status_code}"
        
        print_test("Clear Data", passed, message)
        return passed
    except Exception as e:
        print_test("Clear Data", False, str(e))
        return False

def main():
    """Run all tests"""
    print(f"""
{Colors.BLUE}╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🧪 Bob Sentinel Real-time System Test Suite               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝{Colors.RESET}
""")
    
    print(f"{Colors.YELLOW}Prerequisites:{Colors.RESET}")
    print("  1. Backend must be running: python src/api_server.py")
    print("  2. Install sseclient-py: pip install sseclient-py")
    print()
    
    # Check if sseclient is installed
    try:
        import sseclient
    except ImportError:
        print(f"{Colors.RED}Error: sseclient-py not installed{Colors.RESET}")
        print("Install with: pip install sseclient-py")
        sys.exit(1)
    
    print(f"{Colors.BLUE}Running tests...{Colors.RESET}\n")
    
    results = []
    
    # Run tests
    results.append(("Backend Health", test_backend_health()))
    
    if not results[0][1]:
        print(f"\n{Colors.RED}Backend not running. Cannot continue tests.{Colors.RESET}")
        print(f"Start backend with: {Colors.YELLOW}python src/api_server.py{Colors.RESET}")
        sys.exit(1)
    
    results.append(("REST Endpoints", test_rest_endpoints()))
    results.append(("SSE Connection", test_sse_connection()))
    results.append(("Simulate Attack", test_simulate_attack()))
    results.append(("Real-time Events", test_realtime_events()))
    results.append(("Data Persistence", test_data_persistence()))
    results.append(("Clear Data", test_clear_data()))
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}Test Summary{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = f"{Colors.GREEN}✓{Colors.RESET}" if passed else f"{Colors.RED}✗{Colors.RESET}"
        print(f"{status} {name}")
    
    print(f"\n{Colors.BLUE}Results: {passed_count}/{total_count} tests passed{Colors.RESET}")
    
    if passed_count == total_count:
        print(f"\n{Colors.GREEN}🎉 All tests passed! Real-time system is working correctly.{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Next steps:{Colors.RESET}")
        print("  1. Start frontend: cd frontend && npm run dev")
        print("  2. Open dashboard: http://localhost:5173")
        print("  3. Click 'Simulate Attack' to see real-time updates")
        return 0
    else:
        print(f"\n{Colors.RED}❌ Some tests failed. Please check the errors above.{Colors.RESET}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

# Made with Bob
