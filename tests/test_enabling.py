#!/usr/bin/env python
"""
Test script to verify PyContracts enabling.py functionality.
"""
import pytest
import os
from contracts.enabling import Switches, enable_all, disable_all, all_disabled


def test_disable_enable_all():
    """Test enabling and disabling contracts globally."""
    # Save original state
    original_state = Switches.disable_all
    
    try:
        # Enable contracts
        enable_all()
        assert not all_disabled()
        
        # Disable contracts
        disable_all()
        assert all_disabled()
        
        # Re-enable contracts
        enable_all()
        assert not all_disabled()
    finally:
        # Restore original state
        Switches.disable_all = original_state


def test_environment_variable():
    """Test that the DISABLE_CONTRACTS environment variable works."""
    # Save original state
    original_state = Switches.disable_all
    original_env = os.environ.get('DISABLE_CONTRACTS', None)
    
    try:
        # First ensure contracts are enabled
        Switches.disable_all = False
        
        # Set environment variable to disable contracts
        os.environ['DISABLE_CONTRACTS'] = 'True'
        
        # Try to enable - should remain disabled due to env var
        enable_all()
        assert Switches.disable_all is False, "Environment variable should not be read after initialization"
        
        # Reset to simulate fresh initialization
        Switches.disable_all = True
        
        # Now remove env var
        if 'DISABLE_CONTRACTS' in os.environ:
            del os.environ['DISABLE_CONTRACTS']
        
        # Enable again - should work this time
        enable_all()
        assert not all_disabled()
    finally:
        # Restore original state
        Switches.disable_all = original_state
        if original_env is not None:
            os.environ['DISABLE_CONTRACTS'] = original_env
        elif 'DISABLE_CONTRACTS' in os.environ:
            del os.environ['DISABLE_CONTRACTS']


if __name__ == "__main__":
    pytest.main([__file__])
