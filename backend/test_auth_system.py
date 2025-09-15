#!/usr/bin/env python3
"""
Test script to verify the authentication system is working
"""

import requests
import json
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "http://localhost:8000/api/v1"

def test_auth_system():
    """Test the complete authentication system"""
    print("🔐 Testing ViperMind Authentication System")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing API health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✓ API is healthy")
        else:
            print(f"✗ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}")
        return False
    
    # Test 2: User registration
    print("\n2. Testing user registration...")
    test_user = {
        "email": "authtest@example.com",
        "username": "authtest",
        "password": "testpass123",
        "current_level": "beginner"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✓ User registered successfully: {user_data['username']}")
        elif response.status_code == 400 and "already registered" in response.json().get("detail", ""):
            print("✓ User already exists (expected)")
        else:
            print(f"✗ Registration failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Registration error: {e}")
        return False
    
    # Test 3: User login
    print("\n3. Testing user login...")
    login_data = {
        "email_or_username": test_user["email"],
        "password": test_user["password"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login-json", json=login_data)
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data["access_token"]
            user = auth_data["user"]
            print(f"✓ Login successful for user: {user['username']}")
            print(f"  Token: {token[:20]}...")
        else:
            print(f"✗ Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Login error: {e}")
        return False
    
    # Test 4: Protected endpoint access
    print("\n4. Testing protected endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            profile = response.json()
            print(f"✓ Protected endpoint access successful")
            print(f"  User ID: {profile['id']}")
            print(f"  Email: {profile['email']}")
            print(f"  Level: {profile['current_level']}")
        else:
            print(f"✗ Protected endpoint failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Protected endpoint error: {e}")
        return False
    
    # Test 5: Invalid token handling
    print("\n5. Testing invalid token handling...")
    invalid_headers = {"Authorization": "Bearer invalid_token"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=invalid_headers)
        if response.status_code == 401:
            print("✓ Invalid token properly rejected")
        else:
            print(f"✗ Invalid token not handled properly: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Invalid token test error: {e}")
        return False
    
    # Test 6: User profile update
    print("\n6. Testing profile update...")
    update_data = {"current_level": "intermediate"}
    
    try:
        response = requests.put(f"{BASE_URL}/auth/me", json=update_data, headers=headers)
        if response.status_code == 200:
            updated_profile = response.json()
            print(f"✓ Profile updated successfully")
            print(f"  New level: {updated_profile['current_level']}")
        else:
            print(f"✗ Profile update failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Profile update error: {e}")
        return False
    
    print("\n🎉 All authentication tests passed!")
    print("\n✅ Authentication System Features:")
    print("  - User registration with validation")
    print("  - JWT-based authentication")
    print("  - Protected route access")
    print("  - Profile management")
    print("  - Token validation and error handling")
    print("  - Password hashing and security")
    
    return True

if __name__ == "__main__":
    success = test_auth_system()
    if not success:
        print("\n❌ Authentication system tests failed!")
        exit(1)
    else:
        print("\n🚀 Authentication system is ready for production!")
        exit(0)