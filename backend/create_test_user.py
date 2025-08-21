#!/usr/bin/env python3
"""
Simple script to create a test user for debugging login issues.
This uses the Supabase admin API to create a user directly.
"""

import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

async def create_test_user():
    """Create a test user using Supabase admin API"""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_service_key:
        print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment variables")
        return False
    
    print(f"🔗 Connecting to Supabase: {supabase_url}")
    
    try:
        # Create Supabase client with service role key (admin access)
        supabase: Client = create_client(supabase_url, supabase_service_key)
        
        # Test user credentials
        test_email = "test@example.com"
        test_password = "password123"
        
        print(f"👤 Creating test user: {test_email}")
        
        # Create user using admin API
        response = supabase.auth.admin.create_user({
            "email": test_email,
            "password": test_password,
            "email_confirm": True  # Skip email confirmation
        })
        
        if response.user:
            print(f"✅ Test user created successfully!")
            print(f"   Email: {test_email}")
            print(f"   Password: {test_password}")
            print(f"   User ID: {response.user.id}")
            print(f"   Email confirmed: {response.user.email_confirmed_at is not None}")
            
            # Test login immediately
            print(f"\n🔐 Testing login with created credentials...")
            login_response = supabase.auth.sign_in_with_password({
                "email": test_email,
                "password": test_password
            })
            
            if login_response.user:
                print(f"✅ Login test successful!")
                print(f"   Access token: {login_response.session.access_token[:20]}...")
                return True
            else:
                print(f"❌ Login test failed")
                return False
                
        else:
            print(f"❌ Failed to create user")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        
        # If user already exists, try to update password
        if "already been registered" in str(e) or "already exists" in str(e):
            print(f"🔄 User already exists, trying to update password...")
            try:
                # Get user by email first
                users_response = supabase.auth.admin.list_users()
                test_user = None
                
                for user in users_response:
                    if user.email == test_email:
                        test_user = user
                        break
                
                if test_user:
                    # Update password
                    update_response = supabase.auth.admin.update_user_by_id(
                        test_user.id,
                        {"password": test_password}
                    )
                    
                    if update_response.user:
                        print(f"✅ Password updated successfully!")
                        print(f"   Email: {test_email}")
                        print(f"   Password: {test_password}")
                        
                        # Test login
                        print(f"\n🔐 Testing login with updated credentials...")
                        login_response = supabase.auth.sign_in_with_password({
                            "email": test_email,
                            "password": test_password
                        })
                        
                        if login_response.user:
                            print(f"✅ Login test successful!")
                            return True
                        else:
                            print(f"❌ Login test failed")
                            return False
                else:
                    print(f"❌ Could not find existing user")
                    return False
                    
            except Exception as update_error:
                print(f"❌ Error updating user: {str(update_error)}")
                return False
        else:
            return False

if __name__ == "__main__":
    print("🚀 Creating test user for Suna AI...")
    success = asyncio.run(create_test_user())
    
    if success:
        print(f"\n🎉 Success! You can now login with:")
        print(f"   Email: test@example.com")
        print(f"   Password: password123")
    else:
        print(f"\n❌ Failed to create test user. Check the error messages above.")