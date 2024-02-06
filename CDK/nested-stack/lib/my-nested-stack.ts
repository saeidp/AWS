import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export class MyNestedStack extends cdk.NestedStack {
    constructor( scope: Construct, id: string, props?: cdk.NestedStackProps) {
        super(scope, id, props);

        new s3.Bucket(this, 'MyNestedBucket', {
            versioned: true
        });
    }
}
