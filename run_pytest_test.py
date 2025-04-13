#!/usr/bin/env python
import os
import sys
import pytest

# Add source directory to path
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, src_dir)

if __name__ == "__main__":
    # Default to running 'tests' directory which has been migrated to pytest
    test_path = sys.argv[1] if len(sys.argv) > 1 else 'tests'
    result = pytest.main(["-v", test_path])
    sys.exit(result)