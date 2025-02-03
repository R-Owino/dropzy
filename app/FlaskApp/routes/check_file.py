
import boto3
import logging
from . import upload_bp
from config import Config
from flask_cors import cross_origin
from flask import request, jsonify, session
from werkzeug.utils import secure_filename
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = Config.DYNAMODB_TABLE_NAME

@upload_bp.route("/upload/check-file-exists", methods=["POST"])
@cross_origin(
    origins="*",
    allow_headers=["Content-Type", "Authorization"]
)
def check_file_exists():
    """
    check if a file with the same name already exists in the dynamodb table
    """

    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    file_name = data.get("fileName")

    if not file_name:
        return jsonify({"error": "Invalid request"}), 400
    
    try:
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
