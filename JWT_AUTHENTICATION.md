# JWT Authentication Implementation

This document describes the JWT authentication system implemented in the FinTech application.

## Overview

The application now supports both traditional session-based authentication (for web interface) and JWT token-based authentication (for API access). This provides secure, stateless authentication for API clients while maintaining backward compatibility with the existing web interface.

## Features

- **Dual Authentication**: Supports both session-based (web) and JWT token-based (API) authentication
- **Secure Tokens**: JWT tokens with 24-hour expiration and HMAC-SHA256 signing
- **Protected Routes**: Decorator-based route protection with automatic fallback
- **API-First Design**: JSON responses for API clients, HTML for web clients
- **Backward Compatibility**: Existing web authentication continues to work unchanged

## API Endpoints

### Authentication

#### POST /login
Login with credentials and receive JWT token.

**Request (JSON):**
```json
{
  "role": "user",
  "login_id": "user@example.com",
  "password": "userpassword"
}
```

**Response (Success):**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "USER123",
    "name": "John Doe",
    "role": "user"
  }
}
```

**Response (Error):**
```json
{
  "error": "Invalid password"
}
```

#### POST /logout
Logout (clears session for web clients).

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

### Protected Endpoints

All protected endpoints require authentication via session (web) or JWT token (API).

#### GET /api/user
Get current user information.

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
  "user": {
    "id": "USER123",
    "first_name": "John",
    "last_name": "Doe",
    "role_id": 1,
    "balance": 1500.00,
    "created_at": "2024-01-01T10:00:00"
  }
}
```

#### GET /dashboard
Get dashboard data (JSON for API, HTML for web).

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
  "user": {
    "id": "USER123",
    "name": "John Doe",
    "balance": 1500.00
  },
  "budgets": [...],
  "transactions": [...]
}
```

#### GET /profile
Get user profile (JSON for API, HTML for web).

#### POST /profile
Update user profile.

**Request (JSON):**
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "email": "john.smith@example.com",
  "phone": "+1234567890"
}
```

## Usage Examples

### Python (requests library)

```python
import requests

# Login and get token
login_data = {
    "role": "user",
    "login_id": "user@example.com",
    "password": "userpassword"
}

response = requests.post(
    "http://localhost:5000/login",
    json=login_data,
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    token = response.json()["token"]
    
    # Use token for protected endpoints
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Get user info
    user_response = requests.get(
        "http://localhost:5000/api/user",
        headers=headers
    )
    
    # Get dashboard data
    dashboard_response = requests.get(
        "http://localhost:5000/dashboard",
        headers=headers
    )
```

### JavaScript (fetch API)

```javascript
// Login and get token
const loginData = {
    role: "user",
    login_id: "user@example.com",
    password: "userpassword"
};

fetch("/login", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify(loginData)
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        const token = data.token;
        
        // Store token for future requests
        localStorage.setItem("jwt_token", token);
        
        // Use token for protected endpoints
        return fetch("/api/user", {
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });
    }
})
.then(response => response.json())
.then(userData => {
    console.log("User data:", userData);
});
```

### cURL

```bash
# Login
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"role":"user","login_id":"user@example.com","password":"userpassword"}'

# Use token (replace TOKEN with actual token)
curl -X GET http://localhost:5000/api/user \
  -H "Authorization: Bearer TOKEN"

# Get dashboard data
curl -X GET http://localhost:5000/dashboard \
  -H "Authorization: Bearer TOKEN"
```

## Implementation Details

### JWT Token Structure

Tokens contain the following claims:
- `user_id`: User identifier
- `role_id`: User role identifier
- `exp`: Expiration time (24 hours from issue)
- `iat`: Issued at time

### Security Features

- **HMAC-SHA256 Signing**: Tokens are signed with the application's secret key
- **Expiration**: Tokens automatically expire after 24 hours
- **Stateless**: No server-side token storage required
- **Role-based**: Tokens include role information for authorization

### Backward Compatibility

- Web forms continue to use session-based authentication
- Existing routes work unchanged for web clients
- API clients automatically get JSON responses when using JWT tokens

## Configuration

JWT authentication uses the existing `SECRET_KEY` configuration:

```python
# app/config.py
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
```

For production, ensure `SECRET_KEY` is set to a strong, random value.