import json
import boto3
import ptvsd

print("waiting for debugger... you should start it now")
# # Enable ptvsd on 0.0.0.0 address and on port 5890 that we'll connect later with our IDE
# ptvsd.enable_attach(address=("0.0.0.0", 5890), redirect_output=True)
# ptvsd.wait_for_attach()
# print("debugger attached")


class MyModel(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def save(self):
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.put_object(Bucket="mybucket-12588", Key=self.name, Body=self.value)


def lambda_handler(event, context):
    model_instance = MyModel("steve", "is awesome")
    model_instance.save()
    print("Hello")
    response = {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello world",
                # "location": ip.text.replace("\n", "")
            }
        ),
    }

    return response
