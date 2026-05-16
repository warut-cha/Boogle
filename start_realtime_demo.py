#!/usr/bin/env python3
"""
Bob Sentinel Real-time Demo Startup Script
Starts both backend API server and frontend development server
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🛡️  Bob Sentinel - Real-time Security Dashboard            ║
║                                                               ║
║   Autonomous DevSecOps Assistant with Live Updates           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python dependencies
    try:
        import flask
        import flask_cors
        print("✅ Python dependencies installed")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        print(f"✅ Node.js installed: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js 18+")
        return False
    
    # Check if frontend dependencies are installed
    frontend_path = Path(__file__).parent / "frontend"
    node_modules = frontend_path / "node_modules"
    if not node_modules.exists():
        print("⚠️  Frontend dependencies not installed")
        print("   Installing now...")
        try:
            subprocess.run(['npm', 'install'], cwd=frontend_path, check=True)
            print("✅ Frontend dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install frontend dependencies")
            return False
    else:
        print("✅ Frontend dependencies installed")
    
    return True

def start_backend():
    """Start the Flask backend server"""
    print("\n🚀 Starting Backend API Server...")
    backend_process = subprocess.Popen(
        [sys.executable, 'src/api_server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Wait a bit for server to start
    time.sleep(2)
    
    if backend_process.poll() is None:
        print("✅ Backend server started on http://localhost:8000")
        return backend_process
    else:
        print("❌ Failed to start backend server")
        stdout, stderr = backend_process.communicate()
        print(f"Error: {stderr}")
        return None

def start_frontend():
    """Start the Vite frontend development server"""
    print("\n🚀 Starting Frontend Dashboard...")
    frontend_path = Path(__file__).parent / "frontend"
    
    frontend_process = subprocess.Popen(
        ['npm', 'run', 'dev'],
        cwd=frontend_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Wait for frontend to start
    time.sleep(3)
    
    if frontend_process.poll() is None:
        print("✅ Frontend dashboard started on http://localhost:5173")
        return frontend_process
    else:
        print("❌ Failed to start frontend server")
        return None

def main():
    """Main startup function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing dependencies.")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("Starting Bob Sentinel Real-time System...")
    print("="*60)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("\n❌ Failed to start backend. Exiting.")
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("\n❌ Failed to start frontend. Stopping backend.")
        backend_process.terminate()
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✨ Bob Sentinel is now running!")
    print("="*60)
    print("\n📊 Dashboard: http://localhost:5173")
    print("🔌 API Server: http://localhost:8000")
    print("📡 Real-time Events: http://localhost:8000/api/events")
    print("\n💡 Quick Actions:")
    print("   • Click 'Simulate Attack' in the dashboard to see real-time updates")
    print("   • Watch findings and incidents appear live")
    print("   • View the event log to see SSE messages")
    print("\n⌨️  Press Ctrl+C to stop all services")
    print("="*60 + "\n")
    
    # Open browser
    time.sleep(2)
    try:
        webbrowser.open('http://localhost:5173')
        print("🌐 Opening dashboard in browser...")
    except:
        pass
    
    # Keep running until interrupted
    try:
        while True:
            time.sleep(1)
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("\n⚠️  Backend process stopped unexpectedly")
                break
            if frontend_process.poll() is not None:
                print("\n⚠️  Frontend process stopped unexpectedly")
                break
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down Bob Sentinel...")
        
        # Terminate processes
        print("   Stopping backend...")
        backend_process.terminate()
        backend_process.wait(timeout=5)
        
        print("   Stopping frontend...")
        frontend_process.terminate()
        frontend_process.wait(timeout=5)
        
        print("\n✅ All services stopped. Goodbye!")

if __name__ == '__main__':
    main()

# Made with Bob
