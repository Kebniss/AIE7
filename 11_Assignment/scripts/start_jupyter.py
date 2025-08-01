#!/usr/bin/env python3
"""
Script to start Jupyter with the correct kernel for ManualAIze.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Start Jupyter with the manualaize kernel."""
    print("🚀 Starting Jupyter with ManualAIze kernel...")
    print("📊 Available kernels:")
    
    # List available kernels
    try:
        result = subprocess.run(
            ["uv", "run", "jupyter", "kernelspec", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error listing kernels: {e}")
        return 1
    
    print("\n🎯 Starting Jupyter notebook...")
    print("💡 Tip: Select 'Python (manualaize)' kernel when creating new notebooks")
    print("💡 Tip: Or change kernel in existing notebooks via Kernel > Change kernel")
    
    try:
        # Start Jupyter notebook
        subprocess.run(["uv", "run", "jupyter", "notebook"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Jupyter stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Jupyter: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 