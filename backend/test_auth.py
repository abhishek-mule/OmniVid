import asyncio
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"
TEST_USERNAME = "testuser"

async def test_auth_flow():
    print("🚀 Starting authentication test...")
    
    # Test registration
    print("\n1. Testing user registration...")
    register_data = {
        "username": TEST_USERNAME,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        # Register new user
        register_url = f"{BASE_URL}/auth/register"
        response = requests.post(
            register_url,
            json=register_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ User registered successfully!")
            auth_data = response.json()
            access_token = auth_data["access_token"]
            print(f"Access Token: {access_token[:20]}...")
            
            # Test protected endpoint
            print("\n2. Testing protected endpoint...")
            me_url = f"{BASE_URL}/auth/me"
            headers = {"Authorization": f"Bearer {access_token}"}
            me_response = requests.get(me_url, headers=headers)
            
            if me_response.status_code == 200:
                print("✅ Successfully accessed protected endpoint!")
                print(f"User Info: {json.dumps(me_response.json(), indent=2)}")
                
                # Test login
                print("\n3. Testing login...")
                login_data = {
                    "username": TEST_EMAIL,
                    "password": TEST_PASSWORD,
                }
                
                login_url = f"{BASE_URL}/auth/token"
                login_response = requests.post(
                    login_url,
                    data=login_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    print("✅ Login successful!")
                    print(f"New Access Token: {login_data['access_token'][:20]}...")
                    print("\n🎉 All authentication tests passed successfully!")
                else:
                    print(f"❌ Login failed: {login_response.text}")
            else:
                print(f"❌ Failed to access protected endpoint: {me_response.text}")
        else:
            print(f"❌ Registration failed: {response.text}")
            
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_auth_flow())
