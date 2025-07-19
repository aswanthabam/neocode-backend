#!/usr/bin/env python3
"""
Simple API Test Runner
Tests the core working APIs and generates a comprehensive report
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

class SimpleAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.test_results = []
        
    def log_test(self, test_name, status, response=None, error=None):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "response_status": response.status_code if response else None,
            "response_text": response.text if response else None,
            "error": error
        }
        self.test_results.append(result)
        print(f"[{status.upper()}] {test_name}")
        if error:
            print(f"  Error: {error}")
        if response and response.status_code >= 400:
            print(f"  Response: {response.text}")
    
    def make_request(self, method, endpoint, data=None, headers=None, auth_required=True):
        """Make HTTP request with proper headers"""
        url = f"{API_BASE}{endpoint}"
        
        if headers is None:
            headers = {}
        
        headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        if auth_required and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            return type('Response', (), {'status_code': 0, 'text': str(e)})()
    
    def test_api_documentation(self):
        """Test API documentation endpoints"""
        print("\n=== Testing API Documentation ===")
        
        # Test Swagger UI
        response = self.session.get(f"{BASE_URL}/api/docs/")
        if response.status_code == 200:
            self.log_test("Swagger UI", "PASS", response)
        else:
            self.log_test("Swagger UI", "FAIL", response, f"Status: {response.status_code}")
        
        # Test ReDoc
        response = self.session.get(f"{BASE_URL}/api/redoc/")
        if response.status_code == 200:
            self.log_test("ReDoc", "PASS", response)
        else:
            self.log_test("ReDoc", "FAIL", response, f"Status: {response.status_code}")
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        print("\n=== Testing User Registration ===")
        
        # Test successful registration
        response = self.make_request("POST", "/auth/register/", TEST_USER, auth_required=False)
        if response.status_code == 201:
            data = response.json()
            self.access_token = data.get('tokens', {}).get('access')
            self.refresh_token = data.get('tokens', {}).get('refresh')
            self.log_test("User Registration", "PASS", response)
        else:
            self.log_test("User Registration", "FAIL", response, f"Status: {response.status_code}")
        
        # Test duplicate registration
        response = self.make_request("POST", "/auth/register/", TEST_USER, auth_required=False)
        if response.status_code == 400:
            self.log_test("Duplicate Registration", "PASS", response)
        else:
            self.log_test("Duplicate Registration", "FAIL", response, f"Expected 400, got {response.status_code}")
    
    def test_user_login(self):
        """Test user login endpoint"""
        print("\n=== Testing User Login ===")
        
        # Test successful login
        login_data = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
        response = self.make_request("POST", "/auth/login/", login_data, auth_required=False)
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get('tokens', {}).get('access')
            self.refresh_token = data.get('tokens', {}).get('refresh')
            self.log_test("User Login", "PASS", response)
        else:
            self.log_test("User Login", "FAIL", response, f"Status: {response.status_code}")
        
        # Test invalid credentials
        invalid_data = {
            "email": TEST_USER["email"],
            "password": "wrongpassword"
        }
        response = self.make_request("POST", "/auth/login/", invalid_data, auth_required=False)
        if response.status_code == 400:
            self.log_test("Invalid Login", "PASS", response)
        else:
            self.log_test("Invalid Login", "FAIL", response, f"Expected 400, got {response.status_code}")
    
    def test_user_profile(self):
        """Test user profile endpoints"""
        print("\n=== Testing User Profile ===")
        
        # Test get profile
        response = self.make_request("GET", "/auth/profile/")
        if response.status_code == 200:
            self.log_test("Get Profile", "PASS", response)
        else:
            self.log_test("Get Profile", "FAIL", response, f"Status: {response.status_code}")
        
        # Test update profile
        update_data = {
            "full_name": "Updated Test User",
            "phone_number": "+9876543210",
            "address": "456 Updated Street"
        }
        response = self.make_request("PUT", "/auth/profile/", update_data)
        if response.status_code == 200:
            self.log_test("Update Profile", "PASS", response)
        else:
            self.log_test("Update Profile", "FAIL", response, f"Status: {response.status_code}")
    
    def test_user_stats(self):
        """Test user statistics endpoint"""
        print("\n=== Testing User Statistics ===")
        
        response = self.make_request("GET", "/auth/stats/")
        if response.status_code == 200:
            self.log_test("User Statistics", "PASS", response)
        else:
            self.log_test("User Statistics", "FAIL", response, f"Status: {response.status_code}")
    
    def test_notification_preferences(self):
        """Test notification preferences endpoints"""
        print("\n=== Testing Notification Preferences ===")
        
        # Test get preferences
        response = self.make_request("GET", "/auth/notifications/preferences/")
        if response.status_code == 200:
            self.log_test("Get Notification Preferences", "PASS", response)
        else:
            self.log_test("Get Notification Preferences", "FAIL", response, f"Status: {response.status_code}")
        
        # Test update preferences
        update_data = {
            "email_notifications": True,
            "push_notifications": False,
            "document_shared": True
        }
        response = self.make_request("PUT", "/auth/notifications/preferences/", update_data)
        if response.status_code == 200:
            self.log_test("Update Notification Preferences", "PASS", response)
        else:
            self.log_test("Update Notification Preferences", "FAIL", response, f"Status: {response.status_code}")
    
    def test_privacy_settings(self):
        """Test privacy settings endpoints"""
        print("\n=== Testing Privacy Settings ===")
        
        # Test get settings
        response = self.make_request("GET", "/auth/privacy/settings/")
        if response.status_code == 200:
            self.log_test("Get Privacy Settings", "PASS", response)
        else:
            self.log_test("Get Privacy Settings", "FAIL", response, f"Status: {response.status_code}")
        
        # Test update settings
        update_data = {
            "profile_visibility": "private",
            "show_email": False,
            "allow_document_requests": True
        }
        response = self.make_request("PUT", "/auth/privacy/settings/", update_data)
        if response.status_code == 200:
            self.log_test("Update Privacy Settings", "PASS", response)
        else:
            self.log_test("Update Privacy Settings", "FAIL", response, f"Status: {response.status_code}")
    
    def test_logout(self):
        """Test logout endpoint"""
        print("\n=== Testing Logout ===")
        
        if self.refresh_token:
            logout_data = {"refresh": self.refresh_token}
            response = self.make_request("POST", "/auth/logout/", logout_data)
            if response.status_code == 200:
                self.log_test("Logout", "PASS", response)
            else:
                self.log_test("Logout", "FAIL", response, f"Status: {response.status_code}")
        else:
            self.log_test("Logout", "SKIP", None, "No refresh token available")
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Simple API Test Suite")
        print("=" * 50)
        
        # Test API documentation first
        self.test_api_documentation()
        
        # Test authentication endpoints
        self.test_user_registration()
        self.test_user_login()
        
        # Test protected endpoints
        self.test_user_profile()
        self.test_user_stats()
        self.test_notification_preferences()
        self.test_privacy_settings()
        self.test_logout()
        
        # Generate test report
        self.generate_report()
    
    def generate_report(self):
        """Generate a comprehensive test report"""
        print("\n" + "=" * 50)
        print("📊 TEST REPORT")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        skipped_tests = len([r for r in self.test_results if r['status'] == 'SKIP'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Skipped: {skipped_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Save detailed report
        report_data = {
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": skipped_tests,
                "success_rate": (passed_tests/total_tests)*100
            },
            "tests": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        with open("simple_api_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: simple_api_test_report.json")
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if r['status'] == 'FAIL']
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test.get('error', 'Unknown error')}")
        
        print("\n✅ API Testing Complete!")


if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/docs/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding properly")
            exit(1)
    except requests.exceptions.RequestException:
        print("❌ Server is not running. Please start the Django server first:")
        print("   python manage.py runserver")
        exit(1)
    
    # Run tests
    tester = SimpleAPITester()
    tester.run_all_tests() 