#!/usr/bin/python3

from flask.testing import FlaskClient
import pytest
from unittest.mock import patch
from v1.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_login_get(client: FlaskClient):
    """Test GET /login renders the login page."""
    response = client.get("/api/v1/login")
    assert response.status_code == 200
    assert b"Login to your Account" in response.data


@patch("v1.routes.login.login_user", return_value={
    "Success": True,
    "tokens": {"AccessToken": "mock_access", "IdToken": "mock_id"}
})
def test_login_post_success(mock_login_user, client: FlaskClient):
    """Test successful user login redirects to main page"""
    response = client.post("/api/v1/login", data={
        "email": "testuser@example.com",
        "password": "SecurePass123!"
    })

    assert response.status_code == 302
    assert "/main" in response.location

    with client.session_transaction() as session:
        assert session["email"] == "testuser@example.com"
        assert session["access_token"] == "mock_access"
        assert session["id_token"] == "mock_id"
        assert session["logged_in"] is True


@patch("v1.routes.login.login_user",
       return_value={"Success": False, "message": "Invalid credentials."})
def test_login_post_failure(mock_login_user, client: FlaskClient):
    """Test failed user login re-renders login page"""
    response = client.post("/api/v1/login", data={
        "email": "testuser@example.com",
        "password": "WrongPass"
    })

    assert response.status_code == 200
    assert b"Login to your Account" in response.data
