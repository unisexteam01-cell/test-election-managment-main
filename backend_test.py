#!/usr/bin/env python3
"""
Backend API Testing for Political Voter Management Platform
Tests authentication system with JWT tokens and role-based access control
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend environment
BASE_URL = "https://political-hub-3.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.verify = False  # Disable SSL verification for testing
        # Disable SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.tokens = {}  # Store tokens for different users
        self.users = {}   # Store user data
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def make_request(self, method, endpoint, data=None, headers=None, token=None):
        """Make HTTP request with optional authentication"""
        url = f"{self.base_url}{endpoint}"
        
        # Set default headers
        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)
            
        # Add authorization header if token provided
        if token:
            req_headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=req_headers, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=req_headers, timeout=30)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=req_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            print(f"DEBUG: {method} {url} -> Status: {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request error for {method} {url}: {str(e)}")
            return None
    
    def test_health_endpoints(self):
        """Test health check endpoints"""
        print("\n=== Testing Health Endpoints ===")
        
        # Test root endpoint
        response = self.make_request("GET", "/")
        if response and response.status_code == 200:
            data = response.json()
            if "Political Voter Management Platform API" in data.get("message", ""):
                self.log_test("Root Endpoint", True, "API root endpoint working")
            else:
                self.log_test("Root Endpoint", False, "Unexpected response format", data)
        else:
            self.log_test("Root Endpoint", False, f"Failed to connect: {response.status_code if response else 'No response'}")
        
        # Test health endpoint
        response = self.make_request("GET", "/health")
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                self.log_test("Health Check", True, "Health endpoint working")
            else:
                self.log_test("Health Check", False, "Health status not healthy", data)
        else:
            self.log_test("Health Check", False, f"Health check failed: {response.status_code if response else 'No response'}")
    
    def test_super_admin_creation(self):
        """Test super admin creation (should fail since one exists)"""
        print("\n=== Testing Super Admin Creation ===")
        
        response = self.make_request("POST", "/auth/create-super-admin")
        if response is None:
            self.log_test("Super Admin Creation", False, "No response from server")
        elif response.status_code == 400:
            data = response.json()
            if "Super Admin already exists" in data.get("detail", ""):
                self.log_test("Super Admin Creation", True, "Correctly rejected duplicate super admin creation")
            else:
                self.log_test("Super Admin Creation", False, "Wrong error message", data)
        else:
            self.log_test("Super Admin Creation", False, f"Unexpected status code: {response.status_code}")
    
    def test_login_flow(self):
        """Test login with valid and invalid credentials"""
        print("\n=== Testing Login Flow ===")
        
        # Test valid login
        login_data = {
            "username": "superadmin",
            "password": "admin123"
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        if response and response.status_code == 200:
            data = response.json()
            if "access_token" in data and "user" in data:
                self.tokens["superadmin"] = data["access_token"]
                self.users["superadmin"] = data["user"]
                self.log_test("Valid Login", True, "Super admin login successful")
            else:
                self.log_test("Valid Login", False, "Missing token or user data", data)
        else:
            self.log_test("Valid Login", False, f"Login failed: {response.status_code if response else 'No response'}")
        
        # Test invalid credentials
        invalid_login = {
            "username": "superadmin",
            "password": "wrongpassword"
        }
        
        response = self.make_request("POST", "/auth/login", invalid_login)
        if response is None:
            self.log_test("Invalid Login", False, "No response from server")
        elif response.status_code == 401:
            data = response.json()
            if "Incorrect username or password" in data.get("detail", ""):
                self.log_test("Invalid Login", True, "Correctly rejected invalid credentials")
            else:
                self.log_test("Invalid Login", False, "Wrong error message", data)
        else:
            self.log_test("Invalid Login", False, f"Unexpected status code: {response.status_code}")
        
        # Test non-existent user
        nonexistent_login = {
            "username": "nonexistentuser",
            "password": "anypassword"
        }
        
        response = self.make_request("POST", "/auth/login", nonexistent_login)
        if response is None:
            self.log_test("Non-existent User Login", False, "No response from server")
        elif response.status_code == 401:
            self.log_test("Non-existent User Login", True, "Correctly rejected non-existent user")
        else:
            self.log_test("Non-existent User Login", False, f"Unexpected status code: {response.status_code}")
    
    def test_get_current_user(self):
        """Test get current user endpoint with various scenarios"""
        print("\n=== Testing Get Current User ===")
        
        # Test with valid token
        if "superadmin" in self.tokens:
            response = self.make_request("GET", "/auth/me", token=self.tokens["superadmin"])
            if response and response.status_code == 200:
                data = response.json()
                if data.get("username") == "superadmin" and data.get("role") == "super_admin":
                    self.log_test("Get Current User (Valid Token)", True, "Successfully retrieved user info")
                else:
                    self.log_test("Get Current User (Valid Token)", False, "Incorrect user data", data)
            else:
                self.log_test("Get Current User (Valid Token)", False, f"Failed: {response.status_code if response else 'No response'}")
        else:
            self.log_test("Get Current User (Valid Token)", False, "No valid token available from login test")
        
        # Test without token
        response = self.make_request("GET", "/auth/me")
        if response and response.status_code == 403:
            self.log_test("Get Current User (No Token)", True, "Correctly rejected request without token")
        else:
            self.log_test("Get Current User (No Token)", False, f"Unexpected response: {response.status_code if response else 'No response'}")
        
        # Test with invalid token
        response = self.make_request("GET", "/auth/me", token="invalid_token_12345")
        if response and response.status_code == 401:
            self.log_test("Get Current User (Invalid Token)", True, "Correctly rejected invalid token")
        else:
            self.log_test("Get Current User (Invalid Token)", False, f"Unexpected response: {response.status_code if response else 'No response'}")
    
    def test_user_registration(self):
        """Test role-based user registration"""
        print("\n=== Testing User Registration ===")
        
        if "superadmin" not in self.tokens:
            self.log_test("User Registration Setup", False, "No super admin token available")
            return
        
        # Test: Super Admin creates Admin user
        admin_data = {
            "username": "rajesh_admin",
            "email": "rajesh.admin@political.com",
            "full_name": "Rajesh Kumar",
            "phone": "+91-9876543210",
            "role": "admin",
            "password": "SecurePass123!"
        }
        
        response = self.make_request("POST", "/auth/register", admin_data, token=self.tokens["superadmin"])
        if response and response.status_code == 201:
            data = response.json()
            if data.get("username") == "rajesh_admin" and data.get("role") == "admin":
                self.log_test("Super Admin Creates Admin", True, "Successfully created admin user")
                
                # Login as the new admin to get token
                admin_login = {
                    "username": "rajesh_admin",
                    "password": "SecurePass123!"
                }
                login_response = self.make_request("POST", "/auth/login", admin_login)
                if login_response and login_response.status_code == 200:
                    login_data = login_response.json()
                    self.tokens["rajesh_admin"] = login_data["access_token"]
                    self.users["rajesh_admin"] = login_data["user"]
                    self.log_test("New Admin Login", True, "New admin can login successfully")
                else:
                    self.log_test("New Admin Login", False, "New admin cannot login")
            else:
                self.log_test("Super Admin Creates Admin", False, "Incorrect user data returned", data)
        else:
            self.log_test("Super Admin Creates Admin", False, f"Registration failed: {response.status_code if response else 'No response'}")
        
        # Test: Super Admin tries to create Karyakarta (should fail)
        karyakarta_data = {
            "username": "priya_karyakarta",
            "email": "priya.k@political.com",
            "full_name": "Priya Sharma",
            "phone": "+91-9876543211",
            "role": "karyakarta",
            "password": "SecurePass123!"
        }
        
        response = self.make_request("POST", "/auth/register", karyakarta_data, token=self.tokens["superadmin"])
        if response and response.status_code == 403:
            data = response.json()
            if "Super Admin can only create Admin users" in data.get("detail", ""):
                self.log_test("Super Admin Creates Karyakarta (Should Fail)", True, "Correctly rejected unauthorized role creation")
            else:
                self.log_test("Super Admin Creates Karyakarta (Should Fail)", False, "Wrong error message", data)
        else:
            self.log_test("Super Admin Creates Karyakarta (Should Fail)", False, f"Unexpected response: {response.status_code if response else 'No response'}")
        
        # Test: Admin creates Karyakarta
        if "rajesh_admin" in self.tokens:
            karyakarta_data["username"] = "amit_karyakarta"
            karyakarta_data["email"] = "amit.k@political.com"
            karyakarta_data["full_name"] = "Amit Patel"
            
            response = self.make_request("POST", "/auth/register", karyakarta_data, token=self.tokens["rajesh_admin"])
            if response and response.status_code == 201:
                data = response.json()
                if data.get("username") == "amit_karyakarta" and data.get("role") == "karyakarta":
                    self.log_test("Admin Creates Karyakarta", True, "Successfully created karyakarta user")
                    
                    # Login as the new karyakarta
                    karyakarta_login = {
                        "username": "amit_karyakarta",
                        "password": "SecurePass123!"
                    }
                    login_response = self.make_request("POST", "/auth/login", karyakarta_login)
                    if login_response and login_response.status_code == 200:
                        login_data = login_response.json()
                        self.tokens["amit_karyakarta"] = login_data["access_token"]
                        self.users["amit_karyakarta"] = login_data["user"]
                        self.log_test("New Karyakarta Login", True, "New karyakarta can login successfully")
                    else:
                        self.log_test("New Karyakarta Login", False, "New karyakarta cannot login")
                else:
                    self.log_test("Admin Creates Karyakarta", False, "Incorrect user data returned", data)
            else:
                self.log_test("Admin Creates Karyakarta", False, f"Registration failed: {response.status_code if response else 'No response'}")
            
            # Test: Admin tries to create another Admin (should fail)
            admin_data2 = {
                "username": "another_admin",
                "email": "another.admin@political.com",
                "full_name": "Another Admin",
                "role": "admin",
                "password": "SecurePass123!"
            }
            
            response = self.make_request("POST", "/auth/register", admin_data2, token=self.tokens["rajesh_admin"])
            if response and response.status_code == 403:
                data = response.json()
                if "Admin can only create Karyakarta users" in data.get("detail", ""):
                    self.log_test("Admin Creates Admin (Should Fail)", True, "Correctly rejected unauthorized role creation")
                else:
                    self.log_test("Admin Creates Admin (Should Fail)", False, "Wrong error message", data)
            else:
                self.log_test("Admin Creates Admin (Should Fail)", False, f"Unexpected response: {response.status_code if response else 'No response'}")
    
    def test_list_users(self):
        """Test user listing with role-based filtering"""
        print("\n=== Testing List Users ===")
        
        # Test: Super Admin sees all users
        if "superadmin" in self.tokens:
            response = self.make_request("GET", "/auth/users", token=self.tokens["superadmin"])
            if response and response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) >= 3:  # Should have at least superadmin, admin, karyakarta
                    self.log_test("Super Admin List All Users", True, f"Retrieved {len(data)} users")
                else:
                    self.log_test("Super Admin List All Users", False, f"Unexpected user count: {len(data) if isinstance(data, list) else 'Not a list'}")
            else:
                self.log_test("Super Admin List All Users", False, f"Failed: {response.status_code if response else 'No response'}")
            
            # Test: Super Admin filters by role
            response = self.make_request("GET", "/auth/users?role=admin", token=self.tokens["superadmin"])
            if response and response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    admin_users = [user for user in data if user.get("role") == "admin"]
                    if len(admin_users) == len(data) and len(data) >= 1:
                        self.log_test("Super Admin Filter by Role", True, f"Retrieved {len(data)} admin users")
                    else:
                        self.log_test("Super Admin Filter by Role", False, "Role filtering not working correctly")
                else:
                    self.log_test("Super Admin Filter by Role", False, "Response is not a list")
            else:
                self.log_test("Super Admin Filter by Role", False, f"Failed: {response.status_code if response else 'No response'}")
        
        # Test: Admin sees only their Karyakartas
        if "rajesh_admin" in self.tokens:
            response = self.make_request("GET", "/auth/users", token=self.tokens["rajesh_admin"])
            if response and response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Admin should only see karyakartas assigned to them
                    karyakarta_users = [user for user in data if user.get("role") == "karyakarta"]
                    if len(karyakarta_users) >= 1:
                        self.log_test("Admin List Users", True, f"Admin sees {len(data)} users (their karyakartas)")
                    else:
                        self.log_test("Admin List Users", False, "Admin should see at least one karyakarta")
                else:
                    self.log_test("Admin List Users", False, "Response is not a list")
            else:
                self.log_test("Admin List Users", False, f"Failed: {response.status_code if response else 'No response'}")
    
    def test_user_deactivation(self):
        """Test user deactivation functionality"""
        print("\n=== Testing User Deactivation ===")
        
        if "rajesh_admin" not in self.tokens or "amit_karyakarta" not in self.users:
            self.log_test("User Deactivation Setup", False, "Required users not available")
            return
        
        karyakarta_id = self.users["amit_karyakarta"].get("id") or self.users["amit_karyakarta"].get("_id")
        
        # Test: Admin deactivates their Karyakarta
        response = self.make_request("PUT", f"/auth/users/{karyakarta_id}/deactivate", token=self.tokens["rajesh_admin"])
        if response and response.status_code == 200:
            data = response.json()
            if "deactivated successfully" in data.get("message", ""):
                self.log_test("Admin Deactivates Karyakarta", True, "Successfully deactivated karyakarta")
                
                # Test: Try to login with deactivated account
                deactivated_login = {
                    "username": "amit_karyakarta",
                    "password": "SecurePass123!"
                }
                login_response = self.make_request("POST", "/auth/login", deactivated_login)
                if login_response and login_response.status_code == 403:
                    login_data = login_response.json()
                    if "inactive" in login_data.get("detail", "").lower():
                        self.log_test("Deactivated User Login", True, "Correctly rejected deactivated user login")
                    else:
                        self.log_test("Deactivated User Login", False, "Wrong error message", login_data)
                else:
                    self.log_test("Deactivated User Login", False, f"Unexpected response: {login_response.status_code if login_response else 'No response'}")
            else:
                self.log_test("Admin Deactivates Karyakarta", False, "Unexpected response message", data)
        else:
            self.log_test("Admin Deactivates Karyakarta", False, f"Deactivation failed: {response.status_code if response else 'No response'}")
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Political Voter Management Platform Backend Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Run tests in sequence
        self.test_health_endpoints()
        self.test_super_admin_creation()
        self.test_login_flow()
        self.test_get_current_user()
        self.test_user_registration()
        self.test_list_users()
        self.test_user_deactivation()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for test in self.test_results:
                if not test["success"]:
                    print(f"  • {test['test']}: {test['message']}")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)