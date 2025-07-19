#!/usr/bin/env python3
"""
Docker Test Script for Django OAuth API
This script tests the API endpoints when running in Docker
"""

import requests
import json
import time
import uuid

BASE_URL = "http://localhost:8000/api/auth/"

def wait_for_service(url, max_attempts=30):
    """Wait for the service to be ready"""
    print(f"Waiting for service at {url}...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{url}google/url/", timeout=5)
            if response.status_code == 200:
                print("✅ Service is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"Attempt {attempt + 1}/{max_attempts} - Service not ready yet...")
        time.sleep(2)
    
    print("❌ Service failed to start within expected time")
    return False

def test_register():
    """Test user registration with unique email"""
    print("Testing user registration...")
    
    # Generate unique email to avoid conflicts
    unique_id = str(uuid.uuid4())[:8]
    email = f"docker{unique_id}@example.com"
    
    data = {
        "full_name": "Docker Test User",
        "email": email,
        "username": f"dockeruser{unique_id}",
        "password": "testpassword123",
        "password_confirm": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}register/", json=data)
    print(f"Status: {response.status_code}")
    
    try:
        response_json = response.json()
        print(f"Response: {json.dumps(response_json, indent=2)}")
    except json.JSONDecodeError:
        print(f"Response: {response.text}")
    
    print("-" * 50)
    
    return response_json if response.status_code == 201 else None

def test_login(email):
    """Test user login"""
    print("Testing user login...")
    
    data = {
        "email": email,
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}login/", json=data)
    print(f"Status: {response.status_code}")
    
    try:
        response_json = response.json()
        print(f"Response: {json.dumps(response_json, indent=2)}")
    except json.JSONDecodeError:
        print(f"Response: {response.text}")
    
    print("-" * 50)
    
    return response_json if response.status_code == 200 else None

def test_profile(access_token):
    """Test user profile endpoint"""
    print("Testing user profile...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(f"{BASE_URL}profile/", headers=headers)
    print(f"Status: {response.status_code}")
    
    try:
        response_json = response.json()
        print(f"Response: {json.dumps(response_json, indent=2)}")
    except json.JSONDecodeError:
        print(f"Response: {response.text}")
    
    print("-" * 50)

def test_google_oauth_url():
    """Test Google OAuth URL endpoint"""
    print("Testing Google OAuth URL...")
    
    response = requests.get(f"{BASE_URL}google/url/")
    print(f"Status: {response.status_code}")
    
    try:
        response_json = response.json()
        print(f"Response: {json.dumps(response_json, indent=2)}")
    except json.JSONDecodeError:
        print(f"Response: {response.text}")
    
    print("-" * 50)

def test_token_refresh(refresh_token):
    """Test token refresh"""
    print("Testing token refresh...")
    
    data = {
        "refresh": refresh_token
    }
    
    response = requests.post(f"{BASE_URL}token/refresh/", json=data)
    print(f"Status: {response.status_code}")
    
    try:
        response_json = response.json()
        print(f"Response: {json.dumps(response_json, indent=2)}")
    except json.JSONDecodeError:
        print(f"Response: {response.text}")
    
    print("-" * 50)

def test_logout(access_token, refresh_token):
    """Test logout"""
    print("Testing logout...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    data = {
        "refresh": refresh_token
    }
    
    response = requests.post(f"{BASE_URL}logout/", headers=headers, json=data)
    print(f"Status: {response.status_code}")
    
    try:
        response_json = response.json()
        print(f"Response: {json.dumps(response_json, indent=2)}")
    except json.JSONDecodeError:
        print(f"Response: {response.text}")
    
    print("-" * 50)

def test_health_check():
    """Test basic health check"""
    print("Testing health check...")
    
    try:
        response = requests.get("http://localhost:8000/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    
    print("-" * 50)

def main():
    print("🐳 Docker API Test Suite")
    print("=" * 50)
    
    # Wait for service to be ready
    if not wait_for_service(BASE_URL):
        print("❌ Service is not available. Make sure Docker containers are running.")
        print("Run: docker-compose up --build")
        return
    
    # Test health check
    test_health_check()
    
    # Test registration
    register_result = test_register()
    
    if register_result and 'user' in register_result:
        email = register_result['user']['email']
        
        # Test login
        login_result = test_login(email)
        
        if login_result and 'tokens' in login_result:
            access_token = login_result['tokens']['access']
            refresh_token = login_result['tokens']['refresh']
            
            # Test profile
            test_profile(access_token)
            
            # Test Google OAuth URL
            test_google_oauth_url()
            
            # Test token refresh
            test_token_refresh(refresh_token)
            
            # Test logout
            test_logout(access_token, refresh_token)
            
            print("✅ All Docker tests passed!")
        else:
            print("❌ Login failed, skipping other tests")
    else:
        print("❌ Registration failed, skipping other tests")
    
    print("\n🎉 Docker test suite completed!")

if __name__ == "__main__":
    main() 