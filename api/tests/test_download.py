#!/usr/bin/python3

import pytest
import boto3
from moto import mock_aws
from unittest.mock import patch
from botocore.exceptions import ClientError
from v1.app import app
from v1.config import Config


@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_download_file_unauthorized(client):
    """Test GET /download fails if user is not logged in"""
    response = client.get("/download?file_key=testfile.txt")
    assert response.status_code == 401
    assert response.get_json()["error"] == "Unauthorized"


def test_download_file_missing_file_key(client):
    """Test GET /download fails if file_key parameter is missing"""
    with client.session_transaction() as session:
        session["username"] = "testuser"

    response = client.get("/download")
    assert response.status_code == 400
    assert response.get_json()["error"] == \
        "Missing required parameter: file_key"


@mock_aws
def test_download_file_success(client):
    """Test successful generation of presigned download URL"""
    with client.session_transaction() as session:
        session["username"] = "testuser"

    s3 = boto3.client("s3")
    s3.create_bucket(
        Bucket=Config.S3_BUCKET_NAME,
        CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
    )
    s3.put_object(
        Bucket=Config.S3_BUCKET_NAME,
        Key="documents/testfile.txt",
        Body=b"test content"
    )

    response = client.get("/download?file_key=documents/testfile.txt")
    assert response.status_code == 200
    data = response.get_json()
    assert "presigned_url" in data


@mock_aws
def test_download_file_not_found(client):
    """Test GET /download returns 404 if file does not exist"""
    with client.session_transaction() as session:
        session["username"] = "testuser"

    s3 = boto3.client("s3", )
    s3.create_bucket(
        Bucket=Config.S3_BUCKET_NAME,
        CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
    )

    response = client.get("/download?file_key=documents/missingfile.txt")
    assert response.status_code == 404
    assert response.get_json()["error"] == "File not found"


@patch("boto3.client")
def test_download_file_presigned_url_failure(mock_aws, client):
    """Test GET /download fails if presigned URL generation fails"""
    with client.session_transaction() as session:
        session["username"] = "testuser"

    mock_aws.return_value.generate_presigned_url.side_effect = \
        ClientError({
            "Error": {"Code": "403", "Message": "Forbidden"}},
            "GetObject"
        )

    response = client.get("/download?file_key=documents/testfile.txt")
    assert response.status_code == 500
    assert response.get_json()["error"] == "Failed to generate download URL"


@patch("boto3.client")
def test_download_file_unexpected_error(mock_aws, client):
    """Test GET /download handles unexpected errors gracefully"""
    with client.session_transaction() as session:
        session["username"] = "testuser"

    mock_aws.side_effect = Exception("Unexpected error")

    response = client.get("/download?file_key=documents/testfile.txt")
    assert response.status_code == 500
    assert response.get_json()["error"] == "An unexpected error occured"
