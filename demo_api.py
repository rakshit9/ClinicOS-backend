#!/usr/bin/env python3
"""
FastAPI Authentication API Demo Script
Demonstrates all authentication endpoints
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000"

def make_request(method: str, endpoint: str, data: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
    """Make HTTP request and return JSON response."""
    url = f"{BASE_URL}{endpoint}"
    response = requests.request(method, url, json=data, headers=headers)
    
    try:
        return response.json()
    except:
        return {"status_code": response.status_code, "text": response.text}

def demo_api():
    """Run complete API demo."""
    print("🚀 FastAPI Authentication API Demo")
    print("=" * 40)
    
    # Test data
    email = "demo@example.com"
    password = "DemoPass123!"
    
    # 1. Health Check
    print("\n1. Health Check")
    print("-" * 20)
    health = make_request("GET", "/health")
    print(json.dumps(health, indent=2))
    
    # 2. Register User
    print("\n2. Register New User")
    print("-" * 25)
    register_data = {
        "name": "Demo User",
        "email": email,
        "password": password,
        "role": "doctor"
    }
    register_response = make_request("POST", "/api/auth/register", register_data)
    print(json.dumps(register_response, indent=2))
    
    # Extract tokens
    access_token = register_response.get("tokens", {}).get("access")
    refresh_token = register_response.get("tokens", {}).get("refresh")
    
    # 3. Login User
    print("\n3. Login User")
    print("-" * 15)
    login_data = {
        "email": email,
        "password": password
    }
    login_response = make_request("POST", "/api/auth/login", login_data)
    print(json.dumps(login_response, indent=2))
    
    # Update tokens from login
    access_token = login_response.get("tokens", {}).get("access")
    refresh_token = login_response.get("tokens", {}).get("refresh")
    
    # 4. Get Current User (Protected Route)
    print("\n4. Get Current User (Protected Route)")
    print("-" * 40)
    headers = {"Authorization": f"Bearer {access_token}"}
    me_response = make_request("GET", "/api/auth/me", headers=headers)
    print(json.dumps(me_response, indent=2))
    
    # 5. Refresh Access Token
    print("\n5. Refresh Access Token")
    print("-" * 25)
    refresh_data = {"refreshToken": refresh_token}
    refresh_response = make_request("POST", "/api/auth/refresh", refresh_data)
    print(json.dumps(refresh_response, indent=2))
    
    # Update access token
    access_token = refresh_response.get("access")
    
    # 6. Test Protected Route with New Token
    print("\n6. Test Protected Route with New Token")
    print("-" * 40)
    headers = {"Authorization": f"Bearer {access_token}"}
    me_response = make_request("GET", "/api/auth/me", headers=headers)
    print(json.dumps(me_response, indent=2))
    
    # 7. Forgot Password
    print("\n7. Forgot Password")
    print("-" * 20)
    forgot_data = {"email": email}
    forgot_response = make_request("POST", "/api/auth/forgot-password", forgot_data)
    print(json.dumps(forgot_response, indent=2))
    
    # 8. Logout
    print("\n8. Logout")
    print("-" * 10)
    logout_data = {"refreshToken": refresh_token}
    logout_response = make_request("POST", "/api/auth/logout", logout_data)
    print(f"Status Code: {logout_response.get('status_code', 'N/A')}")
    
    print("\n✅ Demo completed successfully!")
    print("\n📚 Interactive API Documentation:")
    print(f"   Swagger UI: {BASE_URL}/docs")
    print(f"   ReDoc: {BASE_URL}/redoc")

if __name__ == "__main__":
    demo_api()
