#!/usr/bin/env python3
"""
JWT Authentication Demo Script

This script demonstrates how to use the JWT authentication API
endpoints implemented in the FinTech application.

Usage:
1. Start the Flask server: python run.py
2. Run this script: python jwt_demo.py

Note: This requires valid test credentials in the database.
"""

import requests
import json
import time

class FinTechAPIClient:
    """Simple API client for FinTech JWT authentication."""
    
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
    
    def login(self, role, login_id, password):
        """Login and store JWT token."""
        login_data = {
            "role": role,
            "login_id": login_id,
            "password": password
        }
        
        response = self.session.post(
            f"{self.base_url}/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token")
            print(f"✓ Login successful! Token: {self.token[:50]}...")
            return True
        else:
            print(f"✗ Login failed: {response.status_code} - {response.text}")
            return False
    
    def get_headers(self):
        """Get headers with JWT token."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        } if self.token else {"Content-Type": "application/json"}
    
    def get_user_info(self):
        """Get current user information."""
        response = self.session.get(
            f"{self.base_url}/api/user",
            headers=self.get_headers()
        )
        return response
    
    def get_dashboard(self):
        """Get dashboard data."""
        response = self.session.get(
            f"{self.base_url}/dashboard",
            headers=self.get_headers()
        )
        return response
    
    def get_transactions(self):
        """Get user transactions."""
        response = self.session.get(
            f"{self.base_url}/api/transactions",
            headers=self.get_headers()
        )
        return response
    
    def get_budgets(self):
        """Get user budgets."""
        response = self.session.get(
            f"{self.base_url}/api/budgets",
            headers=self.get_headers()
        )
        return response
    
    def send_money(self, recipient_identifier, amount, payment_method="bank", note="API test"):
        """Send money to another user."""
        transaction_data = {
            "recipient_identifier": recipient_identifier,
            "amount": amount,
            "payment_method": payment_method,
            "note": note,
            "location": "API"
        }
        
        response = self.session.post(
            f"{self.base_url}/send-money",
            json=transaction_data,
            headers=self.get_headers()
        )
        return response
    
    def logout(self):
        """Logout and clear token."""
        response = self.session.post(
            f"{self.base_url}/logout",
            headers=self.get_headers()
        )
        self.token = None
        return response

def demo_api_usage():
    """Demonstrate API usage with example calls."""
    print("=== FinTech JWT API Demo ===\n")
    
    # Initialize client
    client = FinTechAPIClient()
    
    # Demo login (replace with actual test credentials)
    print("1. Attempting login...")
    # NOTE: Replace these with actual test credentials from your database
    login_success = client.login(
        role="user",
        login_id="test@example.com",  # Replace with actual test email
        password="testpassword"       # Replace with actual test password
    )
    
    if not login_success:
        print("\n❌ Login failed. Please ensure:")
        print("  - Flask server is running (python run.py)")
        print("  - Database is connected and contains test user")
        print("  - Update login credentials in this script")
        return
    
    print(f"\n2. Testing protected endpoints...")
    
    # Get user info
    print("\n--- User Info ---")
    response = client.get_user_info()
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        user_data = response.json()
        print(f"User: {user_data.get('user', {}).get('first_name', 'N/A')}")
    else:
        print(f"Error: {response.text}")
    
    # Get dashboard
    print("\n--- Dashboard ---")
    response = client.get_dashboard()
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        dashboard_data = response.json()
        print(f"Balance: ${dashboard_data.get('user', {}).get('balance', 'N/A')}")
        print(f"Budgets: {len(dashboard_data.get('budgets', []))}")
        print(f"Transactions: {len(dashboard_data.get('transactions', []))}")
    else:
        print(f"Error: {response.text}")
    
    # Get transactions
    print("\n--- Transactions ---")
    response = client.get_transactions()
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        transactions = response.json()
        print(f"Found {transactions.get('count', 0)} transactions")
    else:
        print(f"Error: {response.text}")
    
    # Get budgets
    print("\n--- Budgets ---")
    response = client.get_budgets()
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        budgets = response.json()
        print(f"Found {budgets.get('count', 0)} budgets")
    else:
        print(f"Error: {response.text}")
    
    # Test logout
    print("\n3. Testing logout...")
    response = client.logout()
    print(f"Logout status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Logout successful")
    
    print(f"\n=== Demo Complete ===")
    print("The JWT authentication system is working! 🎉")

def test_token_validation():
    """Test JWT token validation."""
    print("\n=== Token Validation Test ===")
    
    # Test with invalid token
    headers = {
        "Authorization": "Bearer invalid_token_here",
        "Content-Type": "application/json"
    }
    
    response = requests.get("http://127.0.0.1:5000/api/user", headers=headers)
    print(f"Invalid token test - Status: {response.status_code}")
    
    if response.status_code == 401:
        print("✓ Invalid tokens are properly rejected")
    else:
        print("✗ Token validation issue")

def main():
    """Main demo function."""
    # Check if server is running
    try:
        response = requests.get("http://127.0.0.1:5000/", timeout=2)
        print("✓ Server is running\n")
    except requests.exceptions.RequestException:
        print("❌ Server is not running!")
        print("Please start the Flask server with: python run.py")
        return 1
    
    # Run demo
    demo_api_usage()
    test_token_validation()
    
    return 0

if __name__ == "__main__":
    exit(main())