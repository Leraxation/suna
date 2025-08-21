#!/usr/bin/env python3
"""
Test script to get a real access token and test agent initiation
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_access_token():
    """Get access token by logging in with test user"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_anon_key:
        print("❌ Missing Supabase configuration")
        return None
    
    # Login endpoint
    login_url = f"{supabase_url}/auth/v1/token?grant_type=password"
    
    headers = {
        'apikey': supabase_anon_key,
        'Content-Type': 'application/json'
    }
    
    data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    
    try:
        response = requests.post(login_url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        access_token = result.get('access_token')
        
        if access_token:
            print("✅ Successfully obtained access token")
            return access_token
        else:
            print("❌ No access token in response")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Login failed: {e}")
        return None

def test_agent_initiate(access_token):
    """Test agent initiation with real access token"""
    backend_url = "http://localhost:8000"
    
    # Prepare form data
    form_data = {
        'prompt': 'Hello, this is a test message',
        'model_name': 'claude-3-5-sonnet-20241022',
        'enable_thinking': 'false',
        'stream': 'true'
    }
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        response = requests.post(
            f"{backend_url}/api/agent/initiate",
            headers=headers,
            data=form_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Agent initiation successful!")
            print(f"Thread ID: {result.get('thread_id')}")
            print(f"Agent Run ID: {result.get('agent_run_id')}")
            return True
        else:
            print(f"❌ Agent initiation failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing agent initiation...")
    
    # Get access token
    access_token = get_access_token()
    if not access_token:
        exit(1)
    
    # Test agent initiation
    success = test_agent_initiate(access_token)
    
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed!")
        exit(1)