""" generates a pre-signed URL for downloading a document from S3 """

import boto3
import json
import os
from botocore.exceptions import ClientError
from urllib.parse import unquote_plus

def lambda_handler(event, context):
    try:
        s3 = boto3.client("s3")

        BUCKET_NAME = os.environ("BUCKET_NAME")

        # get the file_key from query parameters
        file_key = unquote_plus(event["queryStringParameters"]["file_key"])

        # check if the object exists in the bucket
        try:
            s3.head_object(Bucket=BUCKET_NAME, Key=file_key)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return {
                    'StatusCode': 404,
                    'headers': {
                        'Contet-Type': 'Application/json',
                        'Allow-Access-Control-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Object not found'
                    })
                }
            raise e
        
        # set url expiration time
        expiration = int(event["queryStringParameters"].get("expiraion", 3600))

        if not (1 <= expiration <= 604800):
            return {
                'StatusCode': 400,
                'headers': {
                    'Contet-Type': 'Application/json',
                    'Allow-Access-Control-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Expiration must be between 1 second and 7 days'
                })
            }
        
        # generate a pre-signed url
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': file_key
            },
            ExpiresIn=expiration
        )

        return {
            'StatusCode': 200,
            'headers': {
                'Contet-Type': 'Application/json',
                'Allow-Access-Control-Origin': '*'
            },
            'body': json.dumps({
                'presigned_url': presigned_url,
                'file_key': file_key
            })
        }
    
    except KeyError as e:
        return {
            'StatusCode': 400,
            'headers': {
                'Contet-Type': 'Application/json',
                'Allow-Access-Control-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Missing required parameter: file_key'
            })
        }
    
    except Exception as e:
        return {
            'StatusCode': 500,
            'headers': {
                'Contet-Type': 'Application/json',
                'Allow-Access-Control-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }
