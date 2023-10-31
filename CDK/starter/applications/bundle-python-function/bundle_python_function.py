import requests

def lambda_handler(event, context):
    response = requests.get("https://httpbin.org/get", timeout=10)
    print(response.json())
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": response.json()
    }