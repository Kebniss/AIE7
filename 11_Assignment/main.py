#!/usr/bin/env python3
"""
ManualAIze - Main entry point for the AI-powered application.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from manualaize import __version__


def main():
    """Main entry point for the ManualAIze application."""
    print("🤖 ManualAIze - AI-powered application for manual processing")
    print(f"Version: {__version__}")
    print("=" * 50)

    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set")
        print("   Please set your OpenAI API key to use AI features")
        print("   You can create a .env file with: OPENAI_API_KEY=your_key_here")
    else:
        print("✅ OpenAI API key is configured")

    print("\n🚀 Ready to start development!")
    print("\nAvailable commands:")
    print("  - python main.py          # Run this application")
    print("  - jupyter notebook        # Start Jupyter notebook")
    print("  - pytest                  # Run tests")
    print("  - black .                 # Format code")
    print("  - isort .                 # Sort imports")
    print("  - flake8 .                # Lint code")
    print("  - mypy .                  # Type check")


if __name__ == "__main__":
    main()
