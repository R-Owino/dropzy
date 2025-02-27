#!/usr/bin/python3

import pytest
from v1.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_logout(client):
    """Test GET /logout clears session and redirects to login"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"
        session["logged_in"] = True

    response = client.get("/api/v1/logout")

    assert response.status_code == 302
    assert "/api/v1/login" in response.location

    with client.session_transaction() as session:
        assert "email" not in session
        assert "logged_in" not in session
