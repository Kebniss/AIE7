#!/usr/bin/env python3
"""
Verify that the ManualAIze Jupyter kernel is properly installed.
"""

import subprocess
import sys
from pathlib import Path


def check_kernel_installation():
    """Check if the manualaize kernel is properly installed."""
    print("🔍 Verifying ManualAIze Jupyter kernel installation...")
    print("=" * 50)
    
    try:
        # Check available kernels
        result = subprocess.run(
            ["uv", "run", "jupyter", "kernelspec", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        
        print("📊 Available Jupyter kernels:")
        print(result.stdout)
        
        # Check if manualaize kernel is in the list
        if "manualaize" in result.stdout:
            print("✅ ManualAIze kernel is properly installed!")
        else:
            print("❌ ManualAIze kernel not found!")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking kernels: {e}")
        return False
    
    # Check kernel spec file
    kernel_path = Path.home() / "Library" / "Jupyter" / "kernels" / "manualaize"
    if kernel_path.exists():
        print(f"✅ Kernel spec found at: {kernel_path}")
    else:
        print(f"❌ Kernel spec not found at: {kernel_path}")
        return False
    
    # Test Python import
    try:
        result = subprocess.run(
            ["uv", "run", "python", "-c", "import ipykernel; print('✅ ipykernel imported successfully')"],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"❌ Error importing ipykernel: {e}")
        return False
    
    print("\n🎉 All checks passed! Your kernel should work in Cursor.")
    print("\n💡 If you're still having issues in Cursor:")
    print("   1. Restart Cursor completely")
    print("   2. Open your notebook")
    print("   3. Select 'Python (manualaize)' from the kernel dropdown")
    print("   4. Or go to Kernel > Change kernel > Python (manualaize)")
    
    return True


if __name__ == "__main__":
    success = check_kernel_installation()
    sys.exit(0 if success else 1) 