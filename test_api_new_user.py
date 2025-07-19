#!/usr/bin/env python3
"""
Test script for Django OAuth Authentication API with new user
Run this script to test all API endpoints with a fresh user
"""

import requests
import json
import uuid

BASE_URL = "http://localhost:8000/api/auth/"

def test_register():
    """Test user registration with unique email"""
    print("Testing user registration...")
    
    # Generate unique email to avoid conflicts
    unique_id = str(uuid.uuid4())[:8]
    email = f"test{unique_id}@example.com"
    
    data = {
        "full_name": "New Test User",
        "email": email,
        "username": f"testuser{unique_id}",
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

def main():
    print("Starting API tests with new user...")
    print("=" * 50)
    
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
        else:
            print("❌ Login failed, skipping other tests")
    else:
        print("❌ Registration failed, skipping other tests")
    
    print("API tests completed!")

if __name__ == "__main__":
    main() 