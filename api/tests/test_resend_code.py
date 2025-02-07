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


def test_resend_verification_no_email(client):
    """Test POST /resend_verification fails if no email in session"""
    response = client.post("/resend_verification")
    assert response.status_code == 400
    assert response.get_json()["success"] is False
    assert response.get_json()["message"] == "No email to verify."


@patch("v1.routes.resend_code.resend_verification_code",
       return_value={"Success": True})
def test_resend_verification_success(mock_resend, client):
    """Test successful resend of verification code."""
    with client.session_transaction() as session:
        session["verification_email"] = "test@example.com"

    response = client.post("/resend_verification")
    assert response.status_code == 200
    assert response.get_json()["success"] is True
    assert response.get_json()["message"] == "Verfication code resent."


@patch("v1.routes.resend_code.resend_verification_code",
       return_value={"Success": False, "message": "Cognito error."})
def test_resend_verification_failure(mock_resend, client):
    """Test failure when resending verification code"""
    with client.session_transaction() as session:
        session["verification_email"] = "test@example.com"

    response = client.post("/resend_verification")
    assert response.status_code == 500
    assert response.get_json()["success"] is False
    assert response.get_json()["message"] == "Cognito error."
