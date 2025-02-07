#!/usr/bin/python3

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


def test_file_metadata_unauthorized(client):
    """Test GET /file-metadata fails if user is not logged in"""
    response = client.get("/file-metadata")
    assert response.status_code == 401
    assert response.get_json()["error"] == "Unauthorized"


@patch("requests.get")
def test_file_metadata_success(mock_get, client):
    """Test successful metadata retrieval"""
    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["id_token"] = "mock_token"

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"files":
                                               ["file1.txt", "file2.txt"]}

    response = client.get("/file-metadata")
    assert response.status_code == 200
    assert response.get_json() == {"files": ["file1.txt", "file2.txt"]}


@patch("requests.get")
def test_file_metadata_api_failure(mock_get, client):
    """Test metadata retrieval failure due to API error"""
    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["id_token"] = "mock_token"

    mock_get.return_value.status_code = 500
    mock_get.return_value.text = "Internal Server Error"

    response = client.get("/file-metadata")
    assert response.status_code == 500
    assert response.get_json()["error"] == \
        "Failed to fetch files: Internal Server Error"


@patch("requests.get",
       side_effect=requests.RequestException("Network failure"))
def test_file_metadata_network_error(mock_get, client):
    """Test metadata retrieval failure due to network error"""
    with client.session_transaction() as session:
        session["username"] = "testuser"
        session["id_token"] = "mock_token"

    response = client.get("/file-metadata")
    assert response.status_code == 500
    assert response.get_json()["error"] == "Network error: Network failure"
