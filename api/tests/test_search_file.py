#!/usr/bin/python3

from flask.testing import FlaskClient
import pytest
import requests
from unittest.mock import patch
from v1.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_search_files_unauthorized(client: FlaskClient):
    """Test GET /search-files fails if user is not logged in"""
    response = client.get("/api/v1/search-files?search=test")
    assert response.status_code == 401
    assert response.get_json()["error"] == "Unauthorized"


def test_search_files_no_search_term(client: FlaskClient):
    """Test GET /search-files fails if search term is missing"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"
        session["id_token"] = "mock_token"

    response = client.get("/api/v1/search-files")
    assert response.status_code == 400
    assert response.get_json()["error"] == "Search term is required"


@patch("requests.get")
def test_search_files_success(mock_get, client: FlaskClient):
    """Test successful file search returns results"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"
        session["id_token"] = "mock_token"

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"files":
                                               ["file1.txt", "file2.txt"]}

    response = client.get("/api/v1/search-files?search=file")
    assert response.status_code == 200
    assert response.get_json() == {"files": ["file1.txt", "file2.txt"]}


@patch("requests.get")
def test_search_files_api_failure(mock_get, client: FlaskClient):
    """Test search file failure due to API error"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"
        session["id_token"] = "mock_token"

    mock_get.return_value.status_code = 500
    mock_get.return_value.text = "Internal Server Error"

    response = client.get("/api/v1/search-files?search=file")
    assert response.status_code == 500
    assert response.get_json()["error"] == \
        "failed to search files: Internal Server Error"


@patch("requests.get",
       side_effect=requests.RequestException("Network failure"))
def test_search_files_network_error(mock_get, client: FlaskClient):
    """Test search file failure due to network error"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"
        session["id_token"] = "mock_token"

    response = client.get("/api/v1/search-files?search=file")
    assert response.status_code == 500
    assert response.get_json()["error"] == "Network error: Network failure"
