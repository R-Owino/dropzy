#!/usr/bin/python3

from unittest.mock import patch
from flask.testing import FlaskClient
import pytest
from v1.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_delete_account_unauthorized(client: FlaskClient):
    """Test account deletion when a user is unauthorized"""
    response = client.post(
        "/api/v1/delete-account",
        headers={"Accept": "application/json"}
    )

    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}


def test_delete_account_success(client: FlaskClient):
    """Test successful account deletion"""
    with patch(
        "v1.routes.delete_account.delete_user",
        return_value={"Success": True}
    ):
        with client.session_transaction() as session:
            session["access_token"] = "valid-access-token"

        response = client.post(
            "/api/v1/delete-account",
            headers={"Accept": "application/json"}
        )
        assert response.status_code == 200
        assert response.json == {"message": "Account deleted successfully."}


def test_delete_account_invalid_token(client: FlaskClient):
    """Test account deletion with an invalid access token"""
    with patch(
        "v1.routes.delete_account.delete_user",
        return_value={"Success": False, "message": "Invalid access token"}
    ):
        with client.session_transaction() as session:
            session["access_token"] = "invalid-access-token"

        response = client.post(
            "/api/v1/delete-account",
            headers={"Accept": "application/json"}
        )

        assert response.status_code == 400
        assert response.json == {"message": "Invalid access token"}


def test_delete_account_cognito_dynamodb_error(client: FlaskClient):
    """Test account deletion when Cognito or DynamoDB returns an error"""
    with patch(
        "v1.routes.delete_account.delete_user",
        return_value={"Success": False, "message": "Internal server error"}
    ):
        with client.session_transaction() as session:
            session["access_token"] = "valid-access-token"

        response = client.post(
            "/api/v1/delete-account",
            headers={"Accept": "application/json"}
        )

        assert response.status_code == 400
        assert response.json == {"message": "Internal server error"}


def test_delete_account_server_error(client: FlaskClient):
    """Test account deletion when an unexpected server error occurs"""
    with patch(
        "v1.routes.delete_account.delete_user",
        side_effect=Exception("Unexpected error")
    ):
        with client.session_transaction() as session:
            session["access_token"] = "valid-access-token"

        response = client.post(
            "/api/v1/delete-account",
            headers={"Accept": "application/json"}
        )

        assert response.status_code == 500
        assert response.json == {"message": "Failed to delete account."}
