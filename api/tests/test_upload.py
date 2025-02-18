#!/usr/bin/python3

from flask.testing import FlaskClient
import pytest
import boto3
from moto import mock_aws
from unittest.mock import patch
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from v1.app import app
from v1.config import Config


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_generate_presigned_url_unauthorized(client: FlaskClient):
    """Test POST /upload/presigned-url fails if user is not logged in"""
    response = client.post("/api/v1/upload/presigned-url", json={})
    assert response.status_code == 401
    assert response.get_json()["error"] == "Unauthorized"


def test_generate_presigned_url_missing_fields(client: FlaskClient):
    """Test POST /upload/presigned-url fails if required fields are missing"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    response = client.post("/api/v1/upload/presigned-url", json={})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid request"


def test_generate_presigned_url_file_too_large(client: FlaskClient):
    """Test POST /upload/presigned-url fails if file size exceeds 2.5GB"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    response = client.post("/api/v1/upload/presigned-url", json={
        "fileName": "largefile.mp4",
        "contentType": "video/mp4",
        "fileSize": 2.6 * 1024 * 1024 * 1024
    })
    assert response.status_code == 400
    assert response.get_json()["error"] == "File size exceeds the max limit"


def test_generate_presigned_url_invalid_filename(client: FlaskClient):
    """Test with malicious/invalid filename"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    response = client.post("/api/v1/upload/presigned-url", json={
        "fileName": "../../../malicious.txt",
        "contentType": "text/plain",
        "fileSize": 1024
    })
    assert response.status_code == 400
    assert "Invalid filename" in response.get_json()["error"]


def test_generate_presigned_url_unsupported_content_type(client: FlaskClient):
    """Test with unsupported content type"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    response = client.post("/api/v1/upload/presigned-url", json={
        "fileName": "test.xyz",
        "contentType": "application/unknown",
        "fileSize": 1024
    })
    assert response.status_code == 400
    assert "Unsupported file type" in response.get_json()["error"]


@mock_aws
def test_generate_presigned_url_success(client: FlaskClient):
    """Test successful generation of presigned URL"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    s3 = boto3.client("s3")
    s3.create_bucket(
        Bucket=Config.S3_BUCKET_NAME,
        CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
    )

    response = client.post("/api/v1/upload/presigned-url", json={
        "fileName": "testfile.txt",
        "contentType": "text/plain",
        "fileSize": 1024
    })

    assert response.status_code == 200
    data = response.get_json()
    assert "url" in data
    assert "key" in data


@patch("boto3.client", side_effect=NoCredentialsError())
def test_generate_presigned_url_no_credentials(mock_aws, client: FlaskClient):
    """Test presigned URL generation fails due to missing credentials"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    response = client.post("/api/v1/upload/presigned-url", json={
        "fileName": "testfile.txt",
        "contentType": "text/plain",
        "fileSize": 1024
    })
    assert response.status_code == 500
    assert "error" in response.get_json()


@patch("boto3.client",
       side_effect=PartialCredentialsError(
           provider="aws",
           cred_var="access_key"))
def test_generate_presigned_url_partial_credentials(
    mock_aws,
    client: FlaskClient
):
    """Test presigned URL generation fails due to partial credentials."""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    response = client.post("/api/v1/upload/presigned-url", json={
        "fileName": "testfile.txt",
        "contentType": "text/plain",
        "fileSize": 1024
    })
    assert response.status_code == 500
    assert "error" in response.get_json()
