#!/usr/bin/env python3
"""
Test script for Django OAuth Authentication API
Run this script to test all API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/auth/"

def test_register():
    """Test user registration"""
    print("Testing user registration...")
    
    data = {
        "full_name": "Test User",
        "email": "test@example.com",
        "username": "testuser",
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

def test_login():
    """Test user login"""
    print("Testing user login...")
    
    data = {
        "email": "test@example.com",
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
    print("Starting API tests...")
    print("=" * 50)
    
    # Test registration
    register_result = test_register()
    
    # Test login
    login_result = test_login()
    
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
    
    print("API tests completed!")

if __name__ == "__main__":
    main() 