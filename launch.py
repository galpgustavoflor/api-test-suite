#!/usr/bin/env python3
"""
Launch script for API Testing Suite.
This script sets up the environment and starts the Streamlit application.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def main():
    """Main function to set up and launch the application."""
    print("🧪 API Testing Suite - Setup and Launch")
    print("=" * 50)
    
    # Check if we're in the correct directory
    current_dir = Path.cwd()
    if not (current_dir / "app.py").exists():
        print("❌ Error: app.py not found in current directory")
        print("Please run this script from the project root directory")
        sys.exit(1)
    
    # Check if Python is available
    try:
        python_version = subprocess.check_output([sys.executable, "--version"], 
                                               text=True).strip()
        print(f"✅ Python found: {python_version}")
    except Exception as e:
        print(f"❌ Error: Python not found: {e}")
        sys.exit(1)
    
    # Set up virtual environment
    venv_path = current_dir / ".venv"
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", ".venv"], 
                         check=True, capture_output=True)
            print("✅ Virtual environment created")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating virtual environment: {e}")
            sys.exit(1)
    else:
        print("✅ Virtual environment already exists")
    
    # Determine the correct Python executable in venv
    if platform.system() == "Windows":
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"
    
    # Upgrade pip
    print("🔧 Upgrading pip...")
    try:
        subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], 
                     check=True, capture_output=True)
        print("✅ Pip upgraded")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Could not upgrade pip: {e}")
    
    # Install requirements
    print("📚 Installing requirements...")
    try:
        subprocess.run([str(pip_exe), "install", "-r", "requirements.txt"], 
                     check=True, capture_output=True)
        print("✅ Requirements installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        sys.exit(1)
    
    # Launch Streamlit
    print("🚀 Starting Streamlit application...")
    print("📖 The application will open in your default browser")
    print("🔗 If it doesn't open automatically, go to: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        # Use the virtual environment's Python to run Streamlit as a module
        subprocess.run([str(python_exe), "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
