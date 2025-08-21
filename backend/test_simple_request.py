#!/usr/bin/env python3
"""
Simple test to check the agent initiate endpoint with detailed error logging
"""

import requests
import json

def test_simple_request():
    """Test a simple request to the agent initiate endpoint"""
    backend_url = "http://localhost:8000"
    
    # Prepare form data
    form_data = {
        'prompt': 'Hello, this is a test message',
        'model_name': 'claude-3-5-sonnet-20241022',
        'enable_thinking': 'false',
        'stream': 'true'
    }
    
    # Use a dummy token for now
    headers = {
        'Authorization': 'Bearer dummy_token'
    }
    
    try:
        response = requests.post(
            f"{backend_url}/api/agent/initiate",
            headers=headers,
            data=form_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response: {response.text}")
        
        return response.status_code == 200
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing simple agent initiation request...")
    test_simple_request()