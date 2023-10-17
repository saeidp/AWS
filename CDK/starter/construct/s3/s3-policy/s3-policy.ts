import { Construct } from "constructs";
import * as iam from 'aws-cdk-lib/aws-iam';
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';


export class S3Policy extends Construct {
    constructor(scope: Construct, id: string) {
        super(scope, id);

        const bucket1 = new s3.Bucket(this, 'bucket-id-1', {
            removalPolicy: cdk.RemovalPolicy.DESTROY,
        });

        // creates a Bucket Policy automatically
        bucket1.addToResourcePolicy(
            new iam.PolicyStatement({
                effect: iam.Effect.ALLOW,
                principals: [new iam.ServicePrincipal('lambda.amazonaws.com')],
                actions: ['s3:GetObject'],
                resources: [`${bucket1.bucketArn}/*`],
            })
        );

        // access the bucket policy
        bucket1.policy?.document.addStatements(
            new iam.PolicyStatement({
                effect: iam.Effect.ALLOW,
                principals: [new iam.ServicePrincipal('lambda.amazonaws.com')],
                actions: ['s3:GetBucketTagging'],
                resources: [bucket1.bucketArn],
            }),
        );

        const bucket2 = new s3.Bucket(this, 'bucket-id-2', {
            removalPolicy: cdk.RemovalPolicy.DESTROY,
        });

        // create the bucket policy
        const bucketPolicy = new s3.BucketPolicy(this, 'bucket-policy-id-2', {
            bucket: bucket2,
        });

        // 👇 add policy statements ot the bucket policy
        bucketPolicy.document.addStatements(
            new iam.PolicyStatement({
                effect: iam.Effect.ALLOW,
                principals: [new iam.ServicePrincipal('lambda.amazonaws.com')],
                actions: ['s3:GetObject'],
                resources: [`${bucket2.bucketArn}/*`],
            }),
        );

    }
}