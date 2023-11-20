import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# dynamodb = boto3.resource('dynamodb', region_name="ap-southeast-2")
session = boto3.Session(profile_name="default", region_name="ap-southeast-2")
# dynamodb = session.client("dynamodb")
dynamodb = session.resource('dynamodb')

# Select the DynamoDB table
table = dynamodb.Table('Person')

# Initialize the scan arguments
scan_kwargs = {
    # Add any filters or configuration here if needed
}

done = False
start_key = None

# Paginate through the scan operation until all items are scanned
while not done:
    if start_key:
        scan_kwargs['ExclusiveStartKey'] = start_key
    response = table.scan(**scan_kwargs)
    items = response.get('Items', [])
    for item in items:
        print(item)
    start_key = response.get('LastEvaluatedKey', None)
    done = start_key is None