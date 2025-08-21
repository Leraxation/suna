#!/usr/bin/env python3
"""
Test script to verify the sandbox bypass logic
"""

import os
import sys
sys.path.append('.')

from utils.config import config
from utils.logger import logger

def test_bypass_conditions():
    """Test the sandbox bypass conditions"""
    print("Testing sandbox bypass conditions...")
    
    print(f"ENV_MODE: {config.ENV_MODE}")
    print(f"ENV_MODE.value: {config.ENV_MODE.value}")
    print(f"DISABLE_SANDBOX_IN_DEV: {config.DISABLE_SANDBOX_IN_DEV}")
    
    # Test the exact condition from the code
    condition1 = config.ENV_MODE.value == "local"
    condition2 = config.DISABLE_SANDBOX_IN_DEV
    both_conditions = condition1 and condition2
    
    print(f"config.ENV_MODE.value == 'local': {condition1}")
    print(f"config.DISABLE_SANDBOX_IN_DEV: {condition2}")
    print(f"Both conditions (should bypass): {both_conditions}")
    
    if both_conditions:
        print("✅ Sandbox bypass conditions are met!")
    else:
        print("❌ Sandbox bypass conditions are NOT met!")
    
    # Also test the Daytona API key
    print(f"DAYTONA_API_KEY: {config.DAYTONA_API_KEY}")
    if config.DAYTONA_API_KEY == "placeholder_key_12345":
        print("⚠️  Daytona API key is a placeholder - this will cause sandbox creation to fail")
    
if __name__ == "__main__":
    test_bypass_conditions()