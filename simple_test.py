#!/usr/bin/env python3
"""
Simple API Test - Core Working APIs
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test data with unique timestamp
timestamp = int(time.time())
TEST_USER = {
    "email": f"testuser{timestamp}@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "full_name": f"Test User {timestamp}",
    "username": f"testuser{timestamp}"
}

def test_user_registration():
    """Test user registration"""
    print("Testing User Registration...")
    
    response = requests.post(
        f"{API_BASE}/auth/register/",
        json=TEST_USER,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        print("✅ User Registration: PASS")
        data = response.json()
        return data.get('tokens', {}).get('access')
    else:
        print(f"❌ User Registration: FAIL - {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_user_login(access_token=None):
    """Test user login"""
    print("Testing User Login...")
    
    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    
    response = requests.post(
        f"{API_BASE}/auth/login/",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        print("✅ User Login: PASS")
        data = response.json()
        return data.get('tokens', {}).get('access')
    else:
        print(f"❌ User Login: FAIL - {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_user_profile(access_token):
    """Test user profile endpoints"""
    print("Testing User Profile...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # Test get profile
    response = requests.get(f"{API_BASE}/auth/profile/", headers=headers)
    if response.status_code == 200:
        print("✅ Get Profile: PASS")
    else:
        print(f"❌ Get Profile: FAIL - {response.status_code}")
    
    # Test update profile
    update_data = {
        "full_name": "Updated Test User",
        "phone_number": "+9876543210"
    }
    response = requests.put(f"{API_BASE}/auth/profile/", json=update_data, headers=headers)
    if response.status_code == 200:
        print("✅ Update Profile: PASS")
    else:
        print(f"❌ Update Profile: FAIL - {response.status_code}")

def test_user_stats(access_token):
    """Test user statistics"""
    print("Testing User Statistics...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(f"{API_BASE}/auth/stats/", headers=headers)
    if response.status_code == 200:
        print("✅ User Statistics: PASS")
    else:
        print(f"❌ User Statistics: FAIL - {response.status_code}")

def test_notification_preferences(access_token):
    """Test notification preferences"""
    print("Testing Notification Preferences...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # Test get preferences
    response = requests.get(f"{API_BASE}/auth/notifications/preferences/", headers=headers)
    if response.status_code == 200:
        print("✅ Get Notification Preferences: PASS")
    else:
        print(f"❌ Get Notification Preferences: FAIL - {response.status_code}")
    
    # Test update preferences
    update_data = {
        "email_notifications": True,
        "push_notifications": False
    }
    response = requests.put(f"{API_BASE}/auth/notifications/preferences/", json=update_data, headers=headers)
    if response.status_code == 200:
        print("✅ Update Notification Preferences: PASS")
    else:
        print(f"❌ Update Notification Preferences: FAIL - {response.status_code}")

def test_privacy_settings(access_token):
    """Test privacy settings"""
    print("Testing Privacy Settings...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # Test get settings
    response = requests.get(f"{API_BASE}/auth/privacy/settings/", headers=headers)
    if response.status_code == 200:
        print("✅ Get Privacy Settings: PASS")
    else:
        print(f"❌ Get Privacy Settings: FAIL - {response.status_code}")
    
    # Test update settings
    update_data = {
        "profile_visibility": "private",
        "show_email": False
    }
    response = requests.put(f"{API_BASE}/auth/privacy/settings/", json=update_data, headers=headers)
    if response.status_code == 200:
        print("✅ Update Privacy Settings: PASS")
    else:
        print(f"❌ Update Privacy Settings: FAIL - {response.status_code}")

def main():
    """Run all tests"""
    print("🚀 Starting Simple API Tests")
    print("=" * 50)
    
    # Test registration
    access_token = test_user_registration()
    
    if access_token:
        # Test login
        access_token = test_user_login(access_token)
        
        if access_token:
            # Test protected endpoints
            test_user_profile(access_token)
            test_user_stats(access_token)
            test_notification_preferences(access_token)
            test_privacy_settings(access_token)
        else:
            print("❌ Cannot proceed without access token")
    else:
        print("❌ Cannot proceed without successful registration")
    
    print("\n✅ API Testing Complete!")

if __name__ == "__main__":
    main() 