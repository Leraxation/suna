#!/usr/bin/env python3
"""
Direct test of agent initiation function to debug sandbox bypass
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config import config
from utils.logger import logger

async def test_direct_agent_call():
    """Test the agent initiation function directly"""
    
    print("🧪 Testing direct agent initiation call...")
    
    # Print configuration
    print(f"ENV_MODE: {config.ENV_MODE.value}")
    print(f"DISABLE_SANDBOX_IN_DEV: {config.DISABLE_SANDBOX_IN_DEV}")
    print(f"Bypass condition: {config.ENV_MODE.value == 'local' and config.DISABLE_SANDBOX_IN_DEV}")
    
    # Test the sandbox creation logic directly
    try:
        from sandbox.sandbox import create_sandbox
        print("✅ Successfully imported create_sandbox function")
        
        # Test the bypass logic
        if config.ENV_MODE.value == "local" and config.DISABLE_SANDBOX_IN_DEV:
            print("✅ Bypass conditions are met - sandbox should be skipped")
            sandbox_id = "dev-sandbox-disabled"
            vnc_url = "http://localhost:6080"
            website_url = "http://localhost:8080"
            token = "dev-token"
            print(f"✅ Bypass values set: sandbox_id={sandbox_id}, vnc_url={vnc_url}")
        else:
            print("❌ Bypass conditions NOT met - sandbox creation would be attempted")
            try:
                # This should fail since we don't have a real Daytona setup
                sandbox = create_sandbox("test-pass", "test-project")
                print(f"❌ Unexpected: sandbox creation succeeded: {sandbox}")
            except Exception as e:
                print(f"✅ Expected: sandbox creation failed: {str(e)}")
        
    except Exception as e:
        print(f"❌ Import or logic test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct_agent_call())