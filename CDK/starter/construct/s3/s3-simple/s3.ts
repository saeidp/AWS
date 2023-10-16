import { Construct } from "constructs";
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';

export interface IS3Props {
    bucketName: string
}

export class S3 extends Construct {
    constructor(scope: Construct, id: string, { bucketName }: IS3Props) {
        super(scope, id);
        new s3.Bucket(this, 'my-construct-s3', {
            bucketName: bucketName,
            versioned: false, // Enable versioning (optional)
            removalPolicy: cdk.RemovalPolicy.DESTROY, // Be cautious with this setting in production
            publicReadAccess: false,
            encryption: s3.BucketEncryption.S3_MANAGED,
            blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
            autoDeleteObjects: true,
            enforceSSL: true,

        });
    }
}