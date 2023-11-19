import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import json
import os

# dynamodb = boto3.resource('dynamodb', region_name="ap-southeast-2")
session = boto3.Session(profile_name="default", region_name="ap-southeast-2")
# dynamodb = session.client("dynamodb")
dynamodb = session.resource('dynamodb')

try:
    table = dynamodb.Table("Person")
    # response = table.put_item(
    #     Item = {
    #         'id': '1',
    #         "name": "John",
    #         "course": "Computer Science"
    #     }
    # )
    file = open(os.path.join(os.path.dirname(__file__), "data.json"), 'r')
    # print(file.read())
    data = json.load(file)
    for person in data['people']:
         response = table.put_item(
         Item = {
            'id': person["id"],
            "name": person["name"],
            "course": person["course"]
        })
         print("Item inserted successfully:", response)


except NoCredentialsError:
        print("Credentials not available")
except IOError:
    print("File not found. Please check the path.")
except ClientError as e:
    print("Client error:", e.response['Error']['Message'])
# except Exception:
#      print("something went wrong")
     


