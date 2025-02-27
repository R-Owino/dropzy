
import boto3
import logging
from . import upload_bp
from v1.config import Config
from flask_cors import cross_origin
from flask import request, jsonify, session
from werkzeug.utils import secure_filename
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@upload_bp.route("/upload/check-file-exists", methods=["POST"])
@cross_origin(
    origins="*",
    allow_headers=["Content-Type", "Authorization"]
)
def check_file_exists():
    """
    check if a file with the same name already exists in the DynamoDB table

    Returns:
        JSON response:
            - 401 Unauthorised: if user is not logged in
            - 400 Bad Request: if fileName is missing in the request
            - 200 OK: JSON containing {'exists': True/False} depending on
                    whether the file exists
            - 500 Internal Server Error: If an AWS credentials error occurs
    """

    if "email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    file_name = data.get("fileName")

    if not file_name:
        return jsonify({"error": "Invalid request"}), 400

    try:
        # initialize DynamoDB resource
        dynamodb = boto3.resource("dynamodb")
        TABLE_NAME = Config.DOCUMENTS_DYNAMODB_TABLE_NAME

        secure_name = secure_filename(file_name)

        # query dynamodb table for files with the same name
        table = dynamodb.Table(TABLE_NAME)
        response = table.scan(
            FilterExpression='file_name = :filename',
            ExpressionAttributeValues={':filename': secure_name}
        )

        exists = len(response.get('Items', [])) > 0

        return jsonify({"exists": exists})

    except (NoCredentialsError, PartialCredentialsError) as e:
        return jsonify({"error": str(e)}), 500
