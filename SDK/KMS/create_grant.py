import boto3
source_session = boto3.Session(profile_name="dmf-dev", region_name="ap-southeast-2")
source_kms = source_session.client("kms")

source_kms.create_grant(
        KeyId= "arn:aws:kms:ap-southeast-2:433802108761:key/6a911911-e12c-48de-a3e8-e37ca8b58b96",
        Name="marketo",
        GranteePrincipal="arn:aws:iam::892988355045:root",
        Operations=[
            "Encrypt",
            "Decrypt",
            "DescribeKey",
            "GenerateDataKey",
        ],
    )

