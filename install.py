#!/usr/bin/env python3
"""
Robot Framework AI Assistant - Installation Script
This script helps you set up the project.
"""

import sys
import subprocess
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error during {description}: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8 or higher.")
        return False

def install_dependencies():
    """Install Python dependencies"""
    return run_command(
        "pip install -r requirements.txt",
        "Installing Python dependencies"
    )

def setup_environment():
    """Set up environment file"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        try:
            # Copy env.example to .env
            with open(env_example, 'r') as source:
                content = source.read()
            
            with open(env_file, 'w') as target:
                target.write(content)
            
            print("✅ Created .env file from env.example")
            print("⚠️  Please edit .env and add your AWS credentials for Bedrock")
            return True
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    else:
        print("❌ env.example file not found")
        return False

def main():
    """Main installation function"""
    print("🤖 Robot Framework AI Assistant - Installation")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    print("\n🔧 Setting up the project...")
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Installation failed at dependency installation")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("\n❌ Installation failed at environment setup")
        sys.exit(1)
    
    print("\n🎉 Installation completed successfully!")
    print("=" * 50)
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your AWS credentials:")
    print("   - AWS_ACCESS_KEY_ID")
    print("   - AWS_SECRET_ACCESS_KEY")
    print("   - AWS_REGION (default: us-east-1)")
    print("2. Ensure you have access to Amazon Bedrock Claude models")
    print("3. Run: python run.py")
    print("4. Open http://localhost:8000 in your browser")
    print("\n📚 For more information, read README.md")

if __name__ == "__main__":
    main() 