""" fetches a file metadata from the documents table """

import boto3
import simplejson as json
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["DYNAMODB_TABLE_NAME"]

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        table = dynamodb.Table(TABLE_NAME)

        # scan the table for the files
        response = table.scan()
        files = response.get("Items", [])
        logger.info(f"Files received: {len(files)}")

        # extract file metadata
        extracted_files = []
        for file in files:
            extracted_files.append({
                "file_name": file.get("file_name", "unknown"),
                "file_key": file.get("file_key", ""),
                "upload_timestamp": file.get("upload_timestamp",
                                             "1970-01-01T00:00:00.000000+00:00"),
                "object_url": file.get("object_url", ""),
                "size_bytes": file.get("size_bytes", 0),
            })

        # sort the files by upload timestamp
        sorted_files = sorted(
            extracted_files,
            key=lambda x: x["upload_timestamp"],
            reverse=True
        )

        # get only the 15 most recent
        recent_files = sorted_files[:15]

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': json.dumps({
                'message': 'Success',
                'files': recent_files
            })
        }
    
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
