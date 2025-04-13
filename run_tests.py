#!/usr/bin/env python
"""
Script to run the PyContracts test suite.
"""
import os
import sys
import subprocess

def main():
    """Run the PyContracts tests."""
    print(f"Running PyContracts tests with Python {sys.version.split()[0]}")
    
    # Determine the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if pytest is installed
    try:
        import pytest
        has_pytest = True
    except ImportError:
        has_pytest = False
        print("Warning: pytest not found. Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov"])
    
    # Add the src directory to the Python path
    src_dir = os.path.join(script_dir, "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    
    # Run the tests
    if has_pytest:
        print("\nRunning tests with pytest...")
        return pytest.main(["-xvs", "--cov=contracts", "tests", "src/contracts/testing"])
    else:
        print("\nRunning tests with pytest (freshly installed)...")
        return subprocess.call([sys.executable, "-m", "pytest", "-xvs", "--cov=contracts", "tests", "src/contracts/testing"])

if __name__ == "__main__":
    sys.exit(main())