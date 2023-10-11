import { CfnOutput, Duration, RemovalPolicy } from 'aws-cdk-lib';
import * as kms from 'aws-cdk-lib/aws-kms';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';


export class KmsSimple extends Construct {
    constructor(scope: Construct, id: string) {
        super(scope, id);

        const key = new kms.Key(this, 'Key', {
            removalPolicy: RemovalPolicy.DESTROY,
            pendingWindow: Duration.days(7),
            alias: 'kms-simple',
            description: 'KMS key for simple demo',
            enableKeyRotation: false,
        });

        const bucket = new s3.Bucket(this, 'Bucket', {
            encryptionKey: key,
            encryption: s3.BucketEncryption.KMS,
            removalPolicy: RemovalPolicy.DESTROY,
        });

        new CfnOutput(this, 'KMS Key ARN', {
            value: key.keyArn,
        })

        new CfnOutput(this, 'Bucket ARN', {
            value: bucket.bucketArn,

        });
    }
}