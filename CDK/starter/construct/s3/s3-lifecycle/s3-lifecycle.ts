// source article: https://bobbyhadz.com/blog/aws-cdk-s3-lifecycle-rules
import { Construct } from "constructs";
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';

/*
The transition to INTELLIGENT_TIERING must come at least 30 days after
the transition to INFREQUENT_ACCESS, if both are set.

The transition to GLACIER must come at least 30 days after the transition to INTELLIGENT_TIERING.

The transition to DEEP_ARCHIVE must come at least 90 days after the transition to GLACIER.
That's because, if we store data in Glacier for less than 90 days, we end up paying for the whole 90 days.
*/

export class S3Lifecycle extends Construct {
    constructor(scope: Construct, id: string) {
        super(scope, id);

        const s3Bucket = new s3.Bucket(this, 's3-bucket', {
            removalPolicy: cdk.RemovalPolicy.DESTROY,
            autoDeleteObjects: true,
            // 👇 set up lifecycle rules
            lifecycleRules: [
                {
                    // apply the rule only to objects that match the prefix
                    // prefix: 'data/',
                    abortIncompleteMultipartUploadAfter: cdk.Duration.days(90),
                    expiration: cdk.Duration.days(365),
                    transitions: [
                        {
                            storageClass: s3.StorageClass.INFREQUENT_ACCESS,
                            transitionAfter: cdk.Duration.days(30),
                        },
                        {
                            storageClass: s3.StorageClass.INTELLIGENT_TIERING,
                            transitionAfter: cdk.Duration.days(60),
                        },
                        {
                            storageClass: s3.StorageClass.GLACIER,
                            transitionAfter: cdk.Duration.days(90),
                        },
                        {
                            storageClass: s3.StorageClass.DEEP_ARCHIVE,
                            transitionAfter: cdk.Duration.days(180),
                        },
                    ],
                },
            ],
        });


        // Day 0	Objects uploaded
        // Day 60	Objects transition to One Zone Infrequent Access
        // Day 90	Objects expire and get deleted from s3 and glacier
        s3Bucket.addLifecycleRule({
            prefix: 'logs/',
            expiration: cdk.Duration.days(90),
            transitions: [
                {
                    storageClass: s3.StorageClass.ONE_ZONE_INFREQUENT_ACCESS,
                    transitionAfter: cdk.Duration.days(60),
                },
            ],
        });

    }
}