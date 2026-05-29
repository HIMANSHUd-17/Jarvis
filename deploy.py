#!/usr/bin/env python3
"""
One-Click Deploy Script for JARVIS
Starts both backend and frontend servers
"""
import os
import sys
import subprocess
import time
import platform
import webbrowser
from pathlib import Path

def get_os():
    """Get current OS"""
    return platform.system()

def check_env_file():
    """Check if .env file exists, create if not"""
    env_path = Path("backend/config/.env")
    env_example = Path("backend/config/.env.example")
    
    if not env_path.exists():
        if env_example.exists():
            with open(env_example, 'r') as f:
                content = f.read()
            with open(env_path, 'w') as f:
                f.write(content)
            print("✓ Created .env file from template")
        else:
            print("⚠ Warning: .env file not found and no template available")

def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Checking dependencies...")
    try:
        import websockets
        import whisper
        import pyttsx3
        print("✓ All dependencies installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("\nInstalling dependencies...")
        os.system("pip install -r backend/requirements.txt")
        return True

def start_backend():
    """Start backend server"""
    print("\n🚀 Starting Backend Server...")
    backend_path = Path("backend/server.py")
    
    if not backend_path.exists():
        print(f"✗ Error: {backend_path} not found")
        return None
    
    # Start backend in new process
    if get_os() == "Windows":
        process = subprocess.Popen(
            [sys.executable, "backend/server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        process = subprocess.Popen(
            [sys.executable, "backend/server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    print(f"✓ Backend started (PID: {process.pid})")
    return process

def start_frontend():
    """Start frontend server"""
    print("\n🎨 Starting Frontend Server...")
    frontend_path = Path("frontend/web/public")
    
    if not frontend_path.exists():
        print(f"✗ Error: {frontend_path} not found")
        return None
    
    # Determine which serve script to use
    if get_os() == "Windows":
        serve_script = frontend_path / "serve.py"
    elif get_os() == "Darwin":  # macOS
        serve_script = frontend_path / "serve.sh"
    else:  # Linux
        serve_script = frontend_path / "serve.py"
    
    if not serve_script.exists():
        print(f"⚠ Warning: {serve_script} not found, using Python")
        serve_script = frontend_path / "serve.py"
    
    if not serve_script.exists():
        print(f"✗ Error: No serve script found at {frontend_path}")
        return None
    
    # Start frontend in new process
    if get_os() == "Windows":
        process = subprocess.Popen(
            [sys.executable, str(serve_script)],
            cwd=str(frontend_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        process = subprocess.Popen(
            ["bash", str(serve_script)],
            cwd=str(frontend_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    print(f"✓ Frontend started (PID: {process.pid})")
    return process

def open_dashboard():
    """Open dashboard in browser"""
    print("\n🌐 Opening dashboard...")
    time.sleep(2)  # Wait for servers to start
    
    url = "http://localhost:8000"
    try:
        webbrowser.open(url)
        print(f"✓ Opened {url}")
    except Exception as e:
        print(f"⚠ Could not open browser: {e}")
        print(f"  Open manually: {url}")

def print_banner():
    """Print welcome banner"""
    print("""
    ╔═══════════════════════════════════════╗
    ║   🤖 JARVIS - Personal Assistant    ║
    ║        ONE-CLICK DEPLOYMENT          ║
    ╚═══════════════════════════════════════╝
    """)

def print_info():
    """Print startup info"""
    print("""
    ✓ Backend: ws://localhost:8765
    ✓ Frontend: http://localhost:8000
    ✓ API Docs: /docs/API.md
    
    💡 Tips:
       - Say "Open Chrome" or "Open Notepad"
       - Type in the chat box for instant responses
       - Send WhatsApp messages to contacts
       - Check logs/jarvis.log for debug info
    """)

def main():
    """Main deployment function"""
    print_banner()
    
    # Check environment
    check_env_file()
    check_dependencies()
    
    # Start servers
    print("\n⚙️  Deploying JARVIS...")
    backend = start_backend()
    frontend = start_frontend()
    
    if not backend or not frontend:
        print("\n✗ Failed to start servers")
        sys.exit(1)
    
    print_info()
    open_dashboard()
    
    print("\n🎉 JARVIS is running! Press Ctrl+C to stop\n")
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping JARVIS...")
        backend.terminate()
        frontend.terminate()
        time.sleep(1)
        backend.kill()
        frontend.kill()
        print("✓ Stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()
