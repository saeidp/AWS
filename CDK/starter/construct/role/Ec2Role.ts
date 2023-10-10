import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

export class Ec2Role extends Construct {
    constructor(scope: Construct, id: string) {
        super(scope, id);

        const ec2Role = new iam.Role(this, 'ec2Role', {
            assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
            roleName: 'ec2Role',
        });

        // Managed policy
        // some managed policies have service-role in the name. i.e.: service-role/AmazonAPIGatewayPushToCloudWatchLogs
        const s3ReadOnlyPolicy = iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonS3ReadOnlyAccess');
        ec2Role.addManagedPolicy(s3ReadOnlyPolicy);

        // Add to new policy
        // creates an AWS:IAM:Policy resource. Name will use the ec2Role id
        ec2Role.addToPolicy(
            new iam.PolicyStatement({
                effect: iam.Effect.ALLOW,
                resources: ['*'],
                actions: ['logs:CreateLogGroup', 'logs:CreateLogStream']
            }))

        // inline policy.
        // The inline policy is created as a separate CF resource and it is attached to the role.
        // Name uses the cw-logs id
        ec2Role.attachInlinePolicy(
            new iam.Policy(this, 'cw-logs', {
                statements: [
                    new iam.PolicyStatement({
                        actions: ['logs:PutLogEvents'],
                        resources: ['*'],
                    })
                ]
            })
        )






    }
}