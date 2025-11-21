"""
Supabase Connection Test Script
Run this to test if your Supabase connection is working properly
"""
import os
import requests
import json

def test_supabase_connection():
    """Test Supabase connectivity and configuration"""
    
    # Get environment variables
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_anon_key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_anon_key:
        print("❌ Error: Missing Supabase environment variables")
        print("Make sure NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY are set")
        return False
    
    print(f"🔍 Testing Supabase connection...")
    print(f"URL: {supabase_url}")
    print(f"Key: {supabase_anon_key[:50]}...")
    
    # Test 1: Basic connectivity
    try:
        response = requests.get(
            f"{supabase_url}/rest/v1/",
            headers={
                'apikey': supabase_anon_key,
                'Authorization': f'Bearer {supabase_anon_key}'
            },
            timeout=10
        )
        print(f"✅ Basic connectivity: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Supabase API is accessible")
        else:
            print(f"❌ API returned status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False
    
    # Test 2: Auth endpoint
    try:
        auth_response = requests.get(
            f"{supabase_url}/auth/v1/settings",
            headers={
                'apikey': supabase_anon_key,
                'Authorization': f'Bearer {supabase_anon_key}'
            },
            timeout=10
        )
        print(f"✅ Auth endpoint: {auth_response.status_code}")
        
        if auth_response.status_code == 200:
            print("✅ Authentication endpoint is working")
        else:
            print(f"❌ Auth endpoint error: {auth_response.text}")
            
    except Exception as e:
        print(f"❌ Auth endpoint failed: {str(e)}")
    
    # Test 3: Test user creation (simulate)
    try:
        signup_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        
        signup_response = requests.post(
            f"{supabase_url}/auth/v1/signup",
            headers={
                'apikey': supabase_anon_key,
                'Authorization': f'Bearer {supabase_anon_key}',
                'Content-Type': 'application/json'
            },
            json=signup_data,
            timeout=10
        )
        
        print(f"✅ Signup test: {signup_response.status_code}")
        
        if signup_response.status_code == 200:
            print("✅ Signup endpoint is working")
            response_data = signup_response.json()
            if 'user' in response_data:
                print("✅ User created successfully")
            else:
                print("⚠️ Signup may require email confirmation")
        else:
            print(f"❌ Signup error: {signup_response.text}")
            
    except Exception as e:
        print(f"❌ Signup test failed: {str(e)}")
    
    print("\n🔧 Common Fixes:")
    print("1. Go to Supabase Dashboard → Authentication → Settings")
    print("2. Add 'http://localhost:3000' to Site URL")
    print("3. Add 'http://localhost:3000/**' to Redirect URLs") 
    print("4. Disable 'Enable email confirmations' for development")
    print("5. Check if Supabase project is active (not paused)")
    
    return True

if __name__ == "__main__":
    test_supabase_connection()