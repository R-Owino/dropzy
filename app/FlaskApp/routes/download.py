import os
import boto3
import logging
from config import Config
from urllib.parse import unquote_plus
from botocore.exceptions import ClientError
from flask import Blueprint, jsonify, request, session

logger = logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

s3 = boto3.client("s3")
BUCKET_NAME = Config.S3_BUCKET_NAME

download_bp = Blueprint("download", __name__)

@download_bp.route("/download", methods=["GET"])
def download_file():
    """
    Generates a pre-signed URL for downloading a file from S3
    """
    logger.info("Download route accessed")

    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
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
                    "ResponseContentDisposition": \
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
