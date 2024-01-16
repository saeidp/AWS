import json
import os
import boto3

s3_client = boto3.client("s3")
bucket_name = "dp-main-curated-dev"
response = s3_client.get_bucket_policy(Bucket=bucket_name)
policy_json = response["Policy"]
# print(policy_json)
policy = json.loads(policy_json)

flag = True
for entry in policy["Statement"]:
    sid = entry.get("Sid", "" )
    if(sid == "QuickSightAnalytics"):
        flag = False

if(flag):
    policy["Statement"].append(
        {
            "Sid": "QuickSightAnalytics",
            "Effect": "Deny",
            "Principal": {
                "AWS": [
                    "arn:aws:iam::892988355045:role/service-role/aws-quicksight-service-role-v0",
                    "arn:aws:iam::892988355045:root",
                ]
            },
            "Action": ["s3:GetObject", "s3:GetObjectVersion"],
            "Resource": ["arn:aws:s3:::dp-main-curated-dev/crm-student-contact/*"],
        }
    )
    print(policy)

    s3_policy_document = json.dumps(policy)
    s3_client.put_bucket_policy(Bucket=bucket_name, Policy=s3_policy_document)



# s3_policy_document = json.dumps(s3_policy)
# source_s3.put_bucket_policy(Bucket=s3_bucket_name, Policy=s3_policy_document)
