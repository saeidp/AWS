import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# dynamodb = boto3.resource('dynamodb', region_name="ap-southeast-2")
session = boto3.Session(profile_name="default", region_name="ap-southeast-2")
# dynamodb = session.client("dynamodb")
dynamodb = session.resource('dynamodb')

# Select the DynamoDB table
table = dynamodb.Table('Person')


# Specify the primary key of the item to delete
primary_key = {'id': '1', 'name': 'John'}  # Replace with the actual primary key

# Delete the item
response = table.delete_item(Key=primary_key)

print(response)


# there is scan way to read all
scan = table.scan()
with table.batch_writer() as batch:
    for each in scan['Items']:
        key = {'id':each['id'], 'name': each['name']}
        batch.delete_item(Key=key)

print("Items deleted successfully.")


# # Create a list of primary keys for the items you want to delete
# primary_keys = [{'id': '2', 'name': 'Jane' }, {'id': '3', 'name': 'James'}]  # Replace with actual primary keys

# # Use a batch writer to delete items
# with table.batch_writer() as batch:
#     for key in primary_keys:
#         batch.delete_item(Key=key)
