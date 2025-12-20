#!/usr/bin/env python3
"""
One-command startup script for Job Application Workflow Dashboard
Starts both backend and frontend servers, then opens the browser
"""
import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    # Check Python packages
    try:
        import fastapi
        import uvicorn
    except ImportError:
        print("❌ Backend dependencies missing. Run: pip install -r requirements.txt")
        return False
    
    # Check Node.js and npm
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Node.js not found. Please install Node.js 18+")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js 18+")
        return False
    
    # Check if frontend node_modules exists
    frontend_dir = Path(__file__).parent / 'frontend'
    if not (frontend_dir / 'node_modules').exists():
        print("⚠️  Frontend dependencies not installed.")
        print("   Installing frontend dependencies...")
        os.chdir(frontend_dir)
        result = subprocess.run(['npm', 'install'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Failed to install frontend dependencies")
            print(result.stderr)
            return False
        os.chdir(Path(__file__).parent)
        print("✅ Frontend dependencies installed")
    
    return True

def start_backend():
    """Start the FastAPI backend server"""
    print("\n🚀 Starting backend server on http://localhost:8000...")
    backend_script = Path(__file__).parent / 'backend' / 'main.py'
    
    # Start backend in a subprocess
    backend_process = subprocess.Popen(
        [sys.executable, str(backend_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Wait a bit and check if it started successfully
    time.sleep(2)
    if backend_process.poll() is not None:
        # Process has terminated
        stdout, stderr = backend_process.communicate()
        print(f"❌ Backend failed to start:")
        print(stderr)
        return None
    
    return backend_process

def start_frontend():
    """Start the React frontend server"""
    print("🎨 Starting frontend server on http://localhost:3000...")
    frontend_dir = Path(__file__).parent / 'frontend'
    
    # Start frontend in a subprocess
    frontend_process = subprocess.Popen(
        ['npm', 'run', 'dev'],
        cwd=str(frontend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Wait a bit and check if it started successfully
    time.sleep(3)
    if frontend_process.poll() is not None:
        # Process has terminated
        stdout, stderr = frontend_process.communicate()
        print(f"❌ Frontend failed to start:")
        print(stderr)
        return None
    
    return frontend_process

def main():
    """Main function to start everything"""
    print("=" * 60)
    print("  Job Application Workflow Dashboard")
    print("  Bhavesh Chainani - Application Pipeline Management")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    if backend_process is None:
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    if frontend_process is None:
        backend_process.terminate()
        sys.exit(1)
    
    # Wait a bit for servers to fully start
    print("\n⏳ Waiting for servers to start...")
    time.sleep(5)
    
    # Open browser
    print("\n🌐 Opening browser...")
    try:
        webbrowser.open('http://localhost:3000')
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("   Please open http://localhost:3000 manually")
    
    print("\n" + "=" * 60)
    print("✅ Dashboard is running!")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print("\n   Press Ctrl+C to stop both servers")
    print("=" * 60 + "\n")
    
    try:
        # Keep script running and monitor processes
        while True:
            time.sleep(1)
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("\n❌ Backend server stopped unexpectedly")
                break
            if frontend_process.poll() is not None:
                print("\n❌ Frontend server stopped unexpectedly")
                break
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()
        
        # Wait for processes to terminate
        backend_process.wait(timeout=5)
        frontend_process.wait(timeout=5)
        
        print("✅ Servers stopped. Goodbye!")

if __name__ == '__main__':
    main()

