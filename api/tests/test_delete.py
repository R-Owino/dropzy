#!/usr/bin/python3

from flask.testing import FlaskClient
import pytest
import requests
from unittest.mock import patch
from v1.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_delete_file_unauthorized(client: FlaskClient):
    """Test DELETE /delete fails if user is not logged in"""
    response = client.delete("/delete?file_key=testfile.txt")
    assert response.status_code == 401
    assert response.get_json()["error"] == "Unauthorized"


def test_delete_file_missing_file_key(client: FlaskClient):
    """Test DELETE /delete fails if file_key parameter is missing"""
    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["id_token"] = "mock_token"

    response = client.delete("/delete")
    assert response.status_code == 400
    assert response.get_json()["error"] == "Missing file_key parameter"


@patch("requests.delete")
def test_delete_file_success(mock_delete, client: FlaskClient):
    """Test successful file deletion returns 200 OK"""
    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["id_token"] = "mock_token"

    mock_delete.return_value.status_code = 200
    mock_delete.return_value.json.return_value = \
        {"message": "File deleted successfully"}

    response = client.delete("/delete?file_key=testfile.txt")
    assert response.status_code == 200
    assert response.get_json() == {"message": "File deleted successfully"}


def test_delete_file_invalid_file_key(client: FlaskClient):
    """Test DELETE /delete with invalid/malformed file key"""
    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["id_token"] = "mock_token"

    response = client.delete("/delete?file_key=../../malicious.txt")
    assert response.status_code == 400
    assert "Invalid file key" in response.get_json()["error"]


@patch("requests.delete")
def test_delete_file_not_found(mock_delete, client: FlaskClient):
    """Test deleting non-existent file"""
    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["id_token"] = "mock_token"

    mock_delete.return_value.status_code = 404
    mock_delete.return_value.json.return_value = {"error": "File not found"}

    response = client.delete("/delete?file_key=nonexistent.txt")
    assert response.status_code == 404
    assert response.get_json()["error"] == "File not found"


@patch("requests.delete")
def test_delete_file_forbidden(mock_delete, client: FlaskClient):
    """Test deleting file without proper permissions"""
    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["id_token"] = "mock_token"

    mock_delete.return_value.status_code = 403
    mock_delete.return_value.json.return_value = {"error": "Access denied"}

    response = client.delete("/delete?file_key=protected.txt")
    assert response.status_code == 403
    assert response.get_json()["error"] == "Access denied"


@patch("requests.delete")
def test_delete_file_api_failure(mock_delete, client: FlaskClient):
    """Test file deletion failure due to API error"""
    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["id_token"] = "mock_token"

    mock_delete.return_value.status_code = 500
    mock_delete.return_value.json.return_value = \
        {"error": "Internal Server Error"}

    response = client.delete("/delete?file_key=testfile.txt")
    assert response.status_code == 500
    assert response.get_json()["error"] == "Internal Server Error"


@patch("requests.delete",
       side_effect=requests.RequestException("Network failure"))
def test_delete_file_network_error(mock_delete, client: FlaskClient):
    """Test file deletion failure due to network error"""
    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["id_token"] = "mock_token"

    response = client.delete("/delete?file_key=testfile.txt")
    assert response.status_code == 500
    assert "Network error" in response.get_json()["error"]
