#!/usr/bin/python3

from flask.testing import FlaskClient
import pytest
from v1.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_main_get_unauthorized(client: FlaskClient):
    """Test GET /main redirects to login if not logged in"""
    response = client.get("/main")
    assert response.status_code == 302
    assert "/login" in response.location


def test_main_get_authorized(client: FlaskClient):
    """Test GET /main renders template when logged in"""
    with client.session_transaction() as session:
        session["logged_in"] = True
        session["username"] = "testuser"
        session["id_token"] = "test_token"

    response = client.get("/main")
    assert response.status_code == 200
    assert b"testuser" in response.data


def test_main_post_unauthorized(client: FlaskClient):
    """Test POST /main redirects to login if not logged in"""
    response = client.post("/main")
    assert response.status_code == 302
    assert "/login" in response.location


def test_main_post_authorized(client: FlaskClient):
    """Test POST /main renders template when logged in"""
    with client.session_transaction() as session:
        session["logged_in"] = True
        session["username"] = "testuser"
        session["id_token"] = "test_token"

    response = client.post("/main")
    assert response.status_code == 200
    assert b"testuser" in response.data
