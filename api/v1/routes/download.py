
import boto3
import logging
from v1.config import Config
from urllib.parse import unquote_plus
from botocore.exceptions import ClientError
from flask import Blueprint, jsonify, request, session

logger = logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Blueprint for file upload route
download_bp = Blueprint("download", __name__)


@download_bp.route("/download", methods=["GET"])
def download_file():
    """
    Generate a pre-signed URL for downloading a file from S3

    GET:
        - Requires user authentication
        - Requires a `file_key` query parameter specifying the file to download
        - Calls S3 to verify the file exists
            before generating the pre-signed URL
        - Handles missing files and errors gracefully

    Returns:
        JSON response:
            - 401 Unauthorised: user not logged in
            - 400 Bad Request: `file_key` is missing
            - 200 OK: generating pre-signed URL successful
            - 404 Not Found: file does not exist in S3
            - 500 Internal Server Error: S3 errors and unexpected failures
    """

    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        s3 = boto3.client("s3")
        BUCKET_NAME = Config.S3_BUCKET_NAME

        file_key = unquote_plus(request.args.get("file_key", ""))

        if not file_key:
            logger.info("Missing file key")
            return jsonify({
                "error": "Missing required parameter: file_key"
            }), 400

        # exract the original file name
        file_name = file_key.split('/')[1]

        # check if the file exists in the bucket
        try:
            s3.head_object(
                Bucket=BUCKET_NAME,
                Key=file_key
            )
        except ClientError as e:
            logger.error(f"S3 error: {str(e)}")
            if e.response["Error"]["Code"] == "404":
                return jsonify({
                    "error": "File not found"
                }), 404
            logger.error(f"S3 error: {str(e)}")
            return jsonify({
                "error": "Error accessing file"
            }), 500

        # generate a pre-signed url with 1 hour expiration time
        try:
            presigned_url = s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": BUCKET_NAME,
                    "Key": file_key,
                    "ResponseContentDisposition":
                        f'attachment; filename="{file_name}"'
                },
                ExpiresIn=3600
            )
            logger.info(f"Generated pre-signed URL: {presigned_url}")

            return jsonify({
                "presigned_url": presigned_url
            }), 200

        except ClientError as e:
            logger.error(f"Error generating pre-signed URL: {str(e)}")
            return jsonify({
                "error": "Failed to generate download URL"
            }), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "An unexpected error occured"
        }), 500
