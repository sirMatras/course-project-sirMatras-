import pytest
from tests.conftest import auth_headers


def test_successful_registration(client):
    """Test successful user registration"""
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "user"
    assert "id" in data


def test_duplicate_email_registration(client):
    """Test registration with duplicate email returns 400"""
    # First registration
    client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "password123"
    })
    
    # Second registration with same email
    response = client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "password456"
    })
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == 400
    assert data["title"] == "Bad Request"
    assert "already registered" in data.get("detail", "")
    assert "correlation_id" in data


def test_successful_login(client):
    """Test successful login returns tokens"""
    # Register first
    client.post("/auth/register", json={
        "email": "login@example.com",
        "password": "password123"
    })
    
    # Login
    response = client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_invalid_credentials_login(client):
    """Test login with invalid credentials returns 401"""
    # Register first
    client.post("/auth/register", json={
        "email": "invalid@example.com",
        "password": "password123"
    })
    
    # Login with wrong password
    response = client.post("/auth/login", json={
        "email": "invalid@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    data = response.json()
    assert data["status"] == 401
    assert data["title"] == "Unauthorized"
    assert "Invalid credentials" in data.get("detail", "")


def test_nonexistent_user_login(client):
    """Test login with non-existent user returns 401"""
    response = client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "password123"
    })
    assert response.status_code == 401
    data = response.json()
    assert data["status"] == 401
    assert data["title"] == "Unauthorized"


def test_token_refresh(client):
    """Test token refresh works"""
    # Register and login
    client.post("/auth/register", json={
        "email": "refresh@example.com",
        "password": "password123"
    })
    
    login_response = client.post("/auth/login", json={
        "email": "refresh@example.com",
        "password": "password123"
    })
    tokens = login_response.json()
    
    # Refresh tokens
    response = client.post("/auth/refresh", json={
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_logout(client):
    """Test logout endpoint"""
    response = client.post("/auth/logout")
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "logged out"


def test_password_validation(client):
    """Test password validation on registration"""
    # Too short password
    response = client.post("/auth/register", json={
        "email": "short@example.com",
        "password": "123"
    })
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == 422
    assert data["title"] == "Input validation error"


def test_email_validation(client):
    """Test email validation on registration"""
    # Invalid email format
    response = client.post("/auth/register", json={
        "email": "invalid-email",
        "password": "password123"
    })
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == 422
    assert data["title"] == "Input validation error"
