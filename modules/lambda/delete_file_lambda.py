""" deletes a file from S3 bucket and a file's metadata from DynamoDB table """

import boto3
import json
import os
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        s3 = boto3.client("s3")
        dynamodb = boto3.resource("dynamodb")

        BUCKET_NAME = os.environ['BUCKET_NAME']
        TABLE_NAME = os.environ['TABLE_NAME']

        file_key = event.get('queryStringParameters', {}).get('file_key')

        if not file_key:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing file_key'})
            }
        
        # delete form s3
        try:
            s3.delete_object(Bucket=BUCKET_NAME, Key=file_key)
        except ClientError as e:
            logger.error(f"S3 deleteion error: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to delete from S3'})
            }
        
        # delete metadata from DynamoDB
        table = dynamodb.Table(TABLE_NAME)
        try:
            # find item with matching file_key
            response = table.scan(
                FilterExpression='file_key = :key',
                ExpressionAttributeValues={':key': file_key}
            )

            items = response.get('Items', [])
            if items:
                table.delete_item(Key={'file_id': items[0]['file_id']})
        except ClientError as e:
            logger.error(f"DynamoDB deleteion error: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to delete from DynamoDB'})
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'File deleted successfully'})
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
