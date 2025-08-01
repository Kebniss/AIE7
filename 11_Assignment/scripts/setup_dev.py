#!/usr/bin/env python3
"""
Development setup script for ManualAIze.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"   Error output: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("🚀 Setting up ManualAIze development environment...")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Sync dependencies
    if not run_command("uv sync", "Installing dependencies"):
        sys.exit(1)
    
    # Install dev dependencies
    if not run_command("uv sync --extra dev", "Installing development dependencies"):
        sys.exit(1)
    
    # Run tests
    if not run_command("uv run pytest tests/ -v", "Running tests"):
        print("⚠️  Tests failed, but continuing with setup...")
    
    # Format code
    if not run_command("uv run black .", "Formatting code"):
        print("⚠️  Code formatting failed, but continuing with setup...")
    
    # Sort imports
    if not run_command("uv run isort .", "Sorting imports"):
        print("⚠️  Import sorting failed, but continuing with setup...")
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("\n📝 Creating .env file...")
        with open(".env", "w") as f:
            f.write("# ManualAIze Environment Variables\n")
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
            f.write("APP_ENV=development\n")
            f.write("DEBUG=true\n")
        print("✅ Created .env file (please update with your actual API keys)")
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Update your .env file with your OpenAI API key")
    print("2. Activate the environment: uv shell")
    print("3. Start developing: python main.py")
    print("4. Run Jupyter: jupyter notebook")


if __name__ == "__main__":
    main() 