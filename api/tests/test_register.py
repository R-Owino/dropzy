#!/usr/bin/python3

import pytest
from unittest.mock import patch
from v1.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_register_get(client):
    """Test GET /register renders the register page"""
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Create Your Account" in response.data


@patch("v1.routes.register.register_user", return_value={"Success": True})
def test_register_post_success(mock_register_user, client):
    """Test successful user registration redirects to confirm page"""
    response = client.post("/register", data={
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePass123!"
    })
    assert response.status_code == 302
    assert "/confirm" in response.location

    with client.session_transaction() as session:
        assert session["verification_email"] == "test@example.com"


@patch("v1.routes.register.register_user", return_value={"Success": False})
def test_register_post_failure(mock_register_user, client):
    """Test failed user registration re-renders register page."""
    response = client.post("/register", data={
        "email": "test@example.com",
        "username": "testuser",
        "password": "WeakPass"
    })
    assert response.status_code == 200
    assert b"Create Your Account" in response.data
