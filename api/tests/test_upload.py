#!/usr/bin/python3

from flask.testing import FlaskClient
import pytest
import boto3
from moto import mock_aws
from unittest.mock import patch
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import requests
from v1.app import app
from v1.config import Config


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


"""TEST /upload/initialize ROUTE"""


def test_initialize_unauthorized(client: FlaskClient):
    """Test POST /upload/initialize fails if user is not logged in"""
    response = client.post("/api/v1/upload/initialize", json={})
    assert response.status_code == 401
    assert response.get_json()["error"] == "Unauthorized"


def test_initialize_missing_fields(client: FlaskClient):
    """Test /upload/initialize endpoint with missing required fields"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    response = client.post("/api/v1/upload/initialize", json={
        "contentType": "text/plain"
    })
    assert response.status_code == 400

    response = client.post("/api/v1/upload/initialize", json={
        "fileName": "test.txt"
    })
    assert response.status_code == 400


def test_initialize_invalid_filename(client: FlaskClient):
    """Test /upload/initialize endpoint with an invalid filename"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    response = client.post("/api/v1/upload/initialize", json={
        "fileName": "../../test.txt",
        "contentType": "text/plain"
    })
    assert response.status_code == 400
    assert "Invalid filename" in response.json["error"]


def test_initialize_unsupported_file_type(client: FlaskClient):
    """Test /upload/initialize endpoint with unsupported file type"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    response = client.post("/api/v1/upload/initialize", json={
        "fileName": "test.xyz",
        "contentType": "application/unknown"
    })

    assert response.status_code == 400
    assert "Unsupported file type" in response.json["error"]


def test_initialize_invalid_content_type_header(client: FlaskClient):
    """Test /upload/initialize endpoint with invalid content type headers"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    response = client.post("/api/v1/upload/initialize",
                           data="invalid",
                           headers={"Content-Type": "text/plain"})
    assert response.status_code == 415


@mock_aws
def test_initialize_success(client: FlaskClient):
    """Test successful initialization of multipart upload session"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    s3 = boto3.client("s3")
    s3.create_bucket(
        Bucket=Config.S3_BUCKET_NAME,
        CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
    )
    response = client.post("/api/v1/upload/initialize", json={
        "fileName": "test.txt",
        "contentType": "text/plain"
    })
    assert response.status_code == 200
    assert "uploadId" in response.json
    assert "key" in response.json


@patch("boto3.client", side_effect=NoCredentialsError())
def test_initialize_aws_credentials_error(mock_boto, client: FlaskClient):
    """Test /upload/initialize endpoint for incorrect AWS credentials"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    response = client.post("/api/v1/upload/initialize", json={
        "fileName": "test.txt",
        "contentType": "text/plain"
    })
    assert response.status_code == 500


"""TEST /upload/chunk-url ROUTE"""


def test_chunk_url_unauthorized(client: FlaskClient):
    """Test POST /upload/chunk-url fails if user is not logged in"""
    response = client.post("/api/v1/upload/chunk-url", json={})
    assert response.status_code == 401


def test_chunk_url_missing_fields(client: FlaskClient):
    """Test /upload/chunk-url endpoint with missing required fields"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    response = client.post("/api/v1/upload/chunk-url", json={
        "uploadId": "123",
        "partNumber": 1
    })
    assert response.status_code == 400

    response = client.post("/api/v1/upload/chunk-url", json={
        "fileName": "test.txt",
        "partNumber": 1
    })
    assert response.status_code == 400

    response = client.post("/api/v1/upload/chunk-url", json={
        "fileName": "test.txt",
        "uploadId": "123"
    })
    assert response.status_code == 400


def test_chunk_url_invalid_part_number(client: FlaskClient):
    """Test /upload/chunk-url endpoint with invalid part numbers"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    response = client.post("/api/v1/upload/chunk-url", json={
        "fileName": "test.txt",
        "uploadId": "123",
        "partNumber": "abc"
    })
    assert response.status_code == 400
    assert "Invalid part number" in response.json["error"]

    response = client.post("/api/v1/upload/chunk-url", json={
        "fileName": "test.txt",
        "uploadId": "123",
        "partNumber": 0
    })
    assert response.status_code == 400
    assert "Invalid part number" in response.json["error"]


@mock_aws
def test_chunk_url_success(client: FlaskClient):
    """Test successful generation of parts' pre-signed URLs"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    s3 = boto3.client("s3")
    s3.create_bucket(
        Bucket=Config.S3_BUCKET_NAME,
        CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
    )

    init_response = client.post("/api/v1/upload/initialize", json={
        "fileName": "test.txt",
        "contentType": "text/plain"
    })
    upload_id = init_response.json["uploadId"]

    response = client.post("/api/v1/upload/chunk-url", json={
        "fileName": "test.txt",
        "uploadId": upload_id,
        "partNumber": 1
    })
    assert response.status_code == 200
    assert "url" in response.json


"""TEST /upload/complete ROUTE"""


def test_complete_unauthorized(client: FlaskClient):
    """Test POST /upload/complete fails if user is not logged in"""
    response = client.post("/api/v1/upload/complete", json={})
    assert response.status_code == 401


def test_complete_missing_fields(client: FlaskClient):
    """Test /upload/complete endpoint with missing required fields"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    response = client.post("/api/v1/upload/complete", json={
        "uploadId": "123",
        "parts": []
    })
    assert response.status_code == 500

    response = client.post("/api/v1/upload/complete", json={
        "key": "test.txt",
        "parts": []
    })
    assert response.status_code == 500

    response = client.post("/api/v1/upload/complete", json={
        "key": "test.txt",
        "uploadId": "123"
    })
    assert response.status_code == 500


def test_complete_invalid_parts(client: FlaskClient):
    """Test /upload/complete endpoint with invalid parts"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    response = client.post("/api/v1/upload/complete", json={
        "key": "test.txt",
        "uploadId": "123",
        "parts": "invalid"
    })
    assert response.status_code == 500

    response = client.post("/api/v1/upload/complete", json={
        "key": "test.txt",
        "uploadId": "123",
        "parts": [{"PartNumber": 1}]
    })
    assert response.status_code == 500


@mock_aws
def test_complete_success(client: FlaskClient):
    """Test successful completion of multipart upload"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    s3 = boto3.client("s3")
    s3.create_bucket(
        Bucket=Config.S3_BUCKET_NAME,
        CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
    )

    init_response = client.post("/api/v1/upload/initialize", json={
        "fileName": "test.txt",
        "contentType": "text/plain"
    })
    upload_id = init_response.json["uploadId"]
    file_key = init_response.json["key"]

    part_response = client.post("/api/v1/upload/chunk-url", json={
        "fileName": "test.txt",
        "uploadId": upload_id,
        "partNumber": 1
    })
    upload_url = part_response.json["url"]

    response = requests.put(
        upload_url,
        data=b"Test content",
        headers={"Content-Type": "text/plain"}
    )
    etag = response.headers["ETag"]

    parts = [{"PartNumber": 1, "ETag": etag}]
    response = client.post("/api/v1/upload/complete", json={
        "key": file_key,
        "uploadId": upload_id,
        "parts": parts
    })
    assert response.status_code == 200
    assert response.json["message"] == "Upload completed successfully"
