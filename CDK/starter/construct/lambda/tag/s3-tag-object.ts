import { Construct } from "constructs";
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import path = require("path");
import { S3EventSource } from "aws-cdk-lib/aws-lambda-event-sources";

export class S3TagObject extends Construct {
    constructor(scope: Construct, id: string,) {
        super(scope, id);
        console.log(path.join(__dirname, '/../../../applications/tagging-lambda'));
        const tagBucket = new s3.Bucket(this, 'my-construct-s3', {
            bucketName: 'my-bucket-name-1258',
            versioned: false, // Enable versioning (optional)
            removalPolicy: cdk.RemovalPolicy.DESTROY, // Be cautious with this setting in production
            publicReadAccess: false,
            encryption: s3.BucketEncryption.S3_MANAGED,
            blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
            autoDeleteObjects: true,
            enforceSSL: true,
        });

        const taggingLambda = new lambda.Function(this, `tagging-lambda`, {
            runtime: lambda.Runtime.PYTHON_3_11,
            memorySize: 1024,
            timeout: cdk.Duration.seconds(5),
            handler: 'tag-object-lambda.handler',
            code: lambda.Code.fromAsset(path.join(__dirname, '/../../../applications/tagging-lambda')),
            environment: {
                TAG_KEY: 'my-key',
                TAG_VALUE: 'my-value'
            }
        });

        tagBucket.grantReadWrite(taggingLambda);

        const putEventSource = new S3EventSource(tagBucket, {
            events: [s3.EventType.OBJECT_CREATED]
        });

        taggingLambda.addEventSource(putEventSource);




    }
}
