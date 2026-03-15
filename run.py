#!/usr/bin/env python3
"""
Robot Framework AI Assistant - Startup Script
Run this script to start the web application.
"""

import sys
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def check_requirements():
    """Check if requirements are installed"""
    try:
        import fastapi
        import uvicorn
        import boto3
        import jinja2
        import pydantic
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check environment setup"""
    env_file = Path(".env")
    if env_file.exists():
        print("✓ Environment file found")
        return True
    else:
        print("⚠ Warning: .env file not found")
        print("Copy env.example to .env and add your AWS credentials for full functionality")
        return True

def main():
    """Main startup function"""
    print("🤖 Robot Framework AI Assistant - Starting...")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment
    check_environment()
    
    # Start the server
    print("\n🚀 Starting server...")
    print("📱 Open your browser to: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 