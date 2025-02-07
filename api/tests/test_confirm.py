#!/usr/bin/python3

import pytest
from unittest.mock import patch
from v1.app import app


@pytest.fixture
def client():
    """
    Create a test client for the Flask application
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_confirm_get_redirects_to_register(client):
    """
    Test GET /confirm redirects to register if email is missing from session
    """
    response = client.get("/confirm")
    assert response.status_code == 302
    assert "/register" in response.location


def test_confirm_get_renders_template(client):
    """
    Test GET /confirm renders confirm.html when email is in session
    """
    with client.session_transaction() as session:
        session["verification_email"] = "test@example.com"

    response = client.get("/confirm")

    assert response.status_code == 200
    assert b"Verify Your Account" in response.data


def test_confirm_post_missing_code(client):
    """
    Test POST /confirm renders confirm.html if code is missing
    """
    with client.session_transaction() as session:
        session["verification_email"] = "test@example.com"

    response = client.post("/confirm", data={})

    assert response.status_code == 200
    assert b"Verify Your Account" in response.data


@patch("v1.routes.confirm.confirm_user", return_value={"Success": True})
def test_confirm_post_success(mock_confirm_user, client):
    """
    Test successful email confirmation redirects to login
    """
    with client.session_transaction() as session:
        session["verification_email"] = "test@example.com"

    response = client.post("/confirm",
                           data={"code": "123456"},
                           headers={"Accept": "application/json"})
    print("Mock called with:", mock_confirm_user.call_args)
    print("Response JSON:", response.get_json())

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert json_data["redirect_url"] == "/login"


def test_confirm_post_already_confirmed(client):
    """
    Test user already confirmed redirects to login
    """
    with client.session_transaction() as session:
        session["verification_email"] = "test@example.com"

    with patch("v1.routes.confirm.confirm_user",
               return_value={
                   "Success": False,
                   "message": "User is already CONFIRMED"}):
        response = client.post("/confirm",
                               data={"code": "123456"},
                               headers={"Accept": "text/html"})

    assert response.status_code == 302
    assert "/login" in response.location


@patch("v1.routes.confirm.confirm_user")
def test_confirm_post_failure(mock_confirm_user, client):
    """
    Test failed email confirmation returns JSON error message
    """
    mock_confirm_user.return_value = {"Success": False,
                                      "message": "Invalid code"}

    with client.session_transaction() as session:
        session["verification_email"] = "test@example.com"

    response = client.post("/confirm",
                           data={"code": "000000"},
                           headers={"Accept": "application/json"})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is False
    assert json_data["message"] == "Invalid code"
