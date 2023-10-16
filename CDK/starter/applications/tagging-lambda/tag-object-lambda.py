import json
import boto3
import os
import logging
import urllib.parse

logger = logging.getLogger()
logger.setLevel(logging.INFO)
HANDLER = logger.handlers[0]
HANDLER.setFormatter(
    logging.Formatter(
        "[%(asctime)s] %(levelname)s:%(name)s:%(message)s\n\r", "%Y-%m-%d %H:%M:%S"
    )
)

def handler(event, context):
    s3_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_object_key = event['Records'][0]['s3']['object']['key']
    tag_key = os.environ.get('TAG_KEY')
    tag_value = os.environ.get('TAG_VALUE')
   
    s3_client = boto3.client('s3')
    s3_object_key = urllib.parse.unquote(s3_object_key)

    print(tag_key, tag_value)
    print(s3_object_key)

    # Add the specified tag to the S3 object
    try:
        s3_client.put_object_tagging(
            Bucket=s3_bucket,
            Key=s3_object_key,
            Tagging={
                'TagSet': [
                    {
                        'Key': tag_key,
                        'Value': tag_value
                    }
                ]
            }
        )
        logger.info(
            f"Tagged S3 object {s3_object_key} in bucket {s3_bucket} with {tag_key}:{tag_value}")
    except Exception as e:
        logger.info(f"Error tagging S3 object: {e}")
