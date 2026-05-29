"""
JARVIS Quick Start Setup Script
Initializes project with dependencies and configuration
"""

import os
import sys
import subprocess
from pathlib import Path

BACKEND_DIR = Path(__file__).parent / "backend"
FRONTEND_DIR = Path(__file__).parent / "frontend" / "web" / "public"

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def run_command(cmd, shell=False):
    """Run shell command"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def setup_backend():
    """Setup backend Python environment"""
    print_header("Setting up Backend Environment")
    
    # Create venv
    venv_path = BACKEND_DIR / "venv"
    if not venv_path.exists():
        print("📦 Creating Python virtual environment...")
        success, stdout, stderr = run_command(
            f"{sys.executable} -m venv {venv_path}"
        )
        if not success:
            print(f"❌ Failed to create venv: {stderr}")
            return False
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment already exists")
    
    # Activate venv and install requirements
    print("\n📚 Installing Python dependencies...")
    
    if sys.platform == "win32":
        pip_cmd = str(venv_path / "Scripts" / "pip.exe")
    else:
        pip_cmd = str(venv_path / "bin" / "pip")
    
    req_file = BACKEND_DIR / "requirements.txt"
    success, stdout, stderr = run_command(f"{pip_cmd} install -r {req_file}")
    
    if not success:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False
    
    print("✅ Dependencies installed")
    
    # Copy .env.example to .env
    env_example = BACKEND_DIR / "config" / ".env.example"
    env_file = BACKEND_DIR / "config" / ".env"
    
    if not env_file.exists() and env_example.exists():
        print("\n📝 Creating .env configuration file...")
        with open(env_example) as f:
            content = f.read()
        with open(env_file, 'w') as f:
            f.write(content)
        print("✅ .env created (Please update with your API keys)")
    
    return True

def setup_frontend():
    """Setup frontend"""
    print_header("Setting up Frontend")
    
    print("✅ Frontend is ready to use!")
    print(f"📁 Location: {FRONTEND_DIR}")
    print("\n🚀 To start frontend server:")
    
    if sys.platform == "win32":
        print(f"   cd {FRONTEND_DIR}")
        print("   python serve.py")
    else:
        print(f"   cd {FRONTEND_DIR}")
        print("   bash serve.sh")
    
    return True

def print_next_steps():
    """Print next steps"""
    print_header("✨ Setup Complete! Next Steps")
    
    print("1️⃣  Configure Backend:")
    print(f"   Edit: {BACKEND_DIR / 'config' / '.env'}")
    print("   Add your GROQ_API_KEY (https://console.groq.com)")
    
    print("\n2️⃣  Start Backend Server:")
    print(f"   cd {BACKEND_DIR}")
    if sys.platform == "win32":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("   python server.py")
    
    print("\n3️⃣  Start Frontend Server (in another terminal):")
    if sys.platform == "win32":
        print(f"   cd {FRONTEND_DIR}")
        print("   python serve.py")
    else:
        print(f"   cd {FRONTEND_DIR}")
        print("   bash serve.sh")
    
    print("\n4️⃣  Open Dashboard:")
    print("   Browser: http://localhost:8000")
    
    print("\n📚 Documentation:")
    print(f"   • README.md - Project overview")
    print(f"   • docs/ARCHITECTURE.md - System design")
    print(f"   • docs/API.md - API reference")
    print(f"   • docs/TROUBLESHOOTING.md - Troubleshooting")
    
    print("\n" + "="*60 + "\n")

def main():
    """Main setup process"""
    print("\n╔════════════════════════════════════════════════════╗")
    print("║        JARVIS - Personal Intelligence System      ║")
    print("║                 Setup Wizard v1.0                 ║")
    print("╚════════════════════════════════════════════════════╝\n")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print(f"❌ Python 3.9+ required (you have {sys.version})")
        sys.exit(1)
    
    # Setup backend
    if not setup_backend():
        print("\n❌ Backend setup failed")
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend():
        print("\n❌ Frontend setup failed")
        sys.exit(1)
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
