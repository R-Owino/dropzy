from flask.testing import FlaskClient
import pytest
import json
from moto import mock_aws
import boto3
from v1.config import Config
from werkzeug.utils import secure_filename
from botocore.exceptions import NoCredentialsError


@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    from v1.app import app
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@mock_aws
def setup_dynamodb():
    """Set up the mock DynamoDB table before running tests"""
    dynamodb = boto3.resource("dynamodb", region_name="us-west-2")
    table_name = Config.DOCUMENTS_DYNAMODB_TABLE_NAME
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "file_name", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "file_name", "AttributeType": "S"}
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5,
                               "WriteCapacityUnits": 5},
    )
    table.wait_until_exists()
    return table


@mock_aws
def test_check_file_exists(client: FlaskClient):
    """Test case for checking if a file exists in DynamoDB"""
    table = setup_dynamodb()

    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    # Insert a file entry into the table
    test_file_name = "test_document.txt"
    table.put_item(Item={"file_name": secure_filename(test_file_name)})

    response = client.post(
        "/api/v1/upload/check-file-exists",
        data=json.dumps({"fileName": test_file_name}),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json["exists"] is True


@mock_aws
def test_check_file_not_exists(client: FlaskClient):
    """Test case for checking if a non-existent file is correctly reported"""
    setup_dynamodb()
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    response = client.post(
        "/api/v1/upload/check-file-exists",
        data=json.dumps({"fileName": "nonexistent.txt"}),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json["exists"] is False


@mock_aws
def test_check_file_unauthorized(client: FlaskClient):
    """Test case for unauthorized access to the endpoint"""
    response = client.post(
        "/api/v1/upload/check-file-exists",
        data=json.dumps({"fileName": "test.txt"}),
        content_type="application/json",
    )
    assert response.status_code == 401
    assert response.json["error"] == "Unauthorized"


@mock_aws
def test_check_file_invalid_request(client: FlaskClient):
    """Test case for handling invalid requests with missing fileName"""
    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    response = client.post(
        "/api/v1/upload/check-file-exists",
        data=json.dumps({}),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.json["error"] == "Invalid request"


@mock_aws
def test_check_file_credentials_error(
    client: FlaskClient,
    monkeypatch: pytest.MonkeyPatch
):
    """Test for simulating AWS credentials error"""
    from v1.routes import check_file

    setup_dynamodb()

    def mock_dynamodb_resource(*args, **kwargs):
        raise NoCredentialsError()

    monkeypatch.setattr(
        "boto3.resource",
        mock_dynamodb_resource
    )

    with client.session_transaction() as session:
        session["email"] = "testuser@example.com"

    response = client.post(
        "/api/v1/upload/check-file-exists",
        data=json.dumps({"fileName": "test.txt"}),
        content_type="application/json",
    )

    assert response.status_code == 500
    assert "error" in response.json
