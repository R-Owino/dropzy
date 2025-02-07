#!/usr/bin/python3

import pytest
from v1.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_landing_page(client):
    """Test GET / renders the landing page"""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Files on Cloud" in response.data
