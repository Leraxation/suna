#!/usr/bin/env python3
"""
Test the actual HTTP endpoint for agent initiation.
"""

import requests
import json

def test_agent_endpoint():
    """Test the agent initiation HTTP endpoint."""
    
    print("🌐 Testing Agent Initiation HTTP Endpoint")
    print("=" * 50)
    
    # Get access token first
    auth_url = "http://localhost:8000/api/auth/login"
    auth_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        print("🔑 Getting access token...")
        auth_response = requests.post(auth_url, json=auth_data)
        print(f"Auth status: {auth_response.status_code}")
        
        if auth_response.status_code == 200:
            token = auth_response.json().get("access_token")
            print("✅ Successfully obtained access token")
        else:
            print(f"❌ Failed to get token: {auth_response.text}")
            return
            
    except Exception as e:
        print(f"❌ Auth request failed: {e}")
        return
    
    # Test agent initiation
    agent_url = "http://localhost:8000/api/agent/initiate"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Use form data instead of JSON
    form_data = {
        "prompt": "Hello, this is a test prompt for debugging",
        "model_name": "claude-3-5-sonnet-20241022",
        "enable_thinking": False,
        "stream": False
    }
    
    try:
        print("📞 Calling agent initiation endpoint...")
        print(f"URL: {agent_url}")
        print(f"Headers: {headers}")
        print(f"Data: {form_data}")
        
        # Use form data instead of JSON
        response = requests.post(agent_url, headers={"Authorization": f"Bearer {token}"}, data=form_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"Response: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ Agent initiation successful!")
        else:
            print("❌ Agent initiation failed!")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_agent_endpoint()