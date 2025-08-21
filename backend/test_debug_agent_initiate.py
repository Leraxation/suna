#!/usr/bin/env python3
"""
Debug test for agent initiation to trace exactly where the failure occurs.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import Request
from agent.api import initiate_agent_with_files
from utils.config import config
from utils.logger import logger
import json

class MockRequest:
    def __init__(self):
        self.headers = {"authorization": "Bearer test-token"}
        self.client = type('obj', (object,), {'host': 'localhost'})()

async def test_agent_initiation():
    """Test agent initiation with detailed debugging."""
    
    print("🔍 Debug Test: Agent Initiation")
    print("=" * 50)
    
    # Print configuration
    print(f"ENV_MODE: {config.ENV_MODE.value}")
    print(f"DISABLE_SANDBOX_IN_DEV: {config.DISABLE_SANDBOX_IN_DEV}")
    print(f"Bypass condition: {config.ENV_MODE.value == 'local' and config.DISABLE_SANDBOX_IN_DEV}")
    print()
    
    try:
        print("📞 Testing sandbox creation logic directly...")
        
        # Test the sandbox creation logic directly
        from sandbox.sandbox import create_sandbox
        import uuid
        
        sandbox_id = None
        sandbox = None
        sandbox_pass = str(uuid.uuid4())
        vnc_url = None
        website_url = None
        token = None
        
        # Skip sandbox creation in local development mode if disabled
        logger.debug(f"ENV_MODE: {config.ENV_MODE.value}, DISABLE_SANDBOX_IN_DEV: {config.DISABLE_SANDBOX_IN_DEV}")
        if config.ENV_MODE.value == "local" and config.DISABLE_SANDBOX_IN_DEV:
            print("✅ Sandbox creation disabled in local development mode")
            sandbox_id = "dev-sandbox-disabled"
            vnc_url = "http://localhost:6080"
            website_url = "http://localhost:8080"
            token = "dev-token"
            print(f"✅ Using bypass values: sandbox_id={sandbox_id}, vnc_url={vnc_url}")
        else:
            try:
                print("🔧 Attempting to create sandbox...")
                logger.debug(f"About to call create_sandbox with sandbox_pass={sandbox_pass}")
                sandbox = create_sandbox(sandbox_pass, "test-project-id")
                sandbox_id = sandbox.id
                print(f"✅ Created sandbox: {sandbox_id}")
                
                # Get preview links
                vnc_link = sandbox.get_preview_link(6080)
                website_link = sandbox.get_preview_link(8080)
                vnc_url = vnc_link.url if hasattr(vnc_link, 'url') else str(vnc_link).split("url='")[1].split("'")[0]
                website_url = website_link.url if hasattr(website_link, 'url') else str(website_link).split("url='")[1].split("'")[0]
                if hasattr(vnc_link, 'token'):
                    token = vnc_link.token
                elif "token='" in str(vnc_link):
                    token = str(vnc_link).split("token='")[1].split("'")[0]
                    
                print(f"✅ Sandbox URLs: vnc={vnc_url}, website={website_url}")
            except Exception as e:
                print(f"❌ Error creating sandbox: {str(e)}")
                
                # In development mode, continue without sandbox if creation fails
                logger.debug(f"Exception handler - ENV_MODE: {config.ENV_MODE.value}, DISABLE_SANDBOX_IN_DEV: {config.DISABLE_SANDBOX_IN_DEV}")
                if config.ENV_MODE.value == "local" and config.DISABLE_SANDBOX_IN_DEV:
                    print("✅ Sandbox creation failed in dev mode, continuing without sandbox")
                    sandbox_id = "dev-sandbox-disabled"
                    vnc_url = "http://localhost:6080"
                    website_url = "http://localhost:8080"
                    token = "dev-token"
                    print(f"✅ Using fallback values: sandbox_id={sandbox_id}, vnc_url={vnc_url}")
                else:
                    raise Exception("Failed to create sandbox")
        
        print(f"\n✅ Final sandbox configuration:")
        print(f"   sandbox_id: {sandbox_id}")
        print(f"   vnc_url: {vnc_url}")
        print(f"   website_url: {website_url}")
        print(f"   token: {token}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print(f"Exception type: {type(e).__name__}")
        
        # Print full traceback
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent_initiation())