import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';
import { readFileSync } from 'fs';

export class EC2 extends Construct {
    constructor(scope: Construct, id: string) {
        super(scope, id);

        const vpc = new ec2.Vpc(this, 'my-vpc', {
            ipAddresses: ec2.IpAddresses.cidr('10.0.0.0/16'),
            natGateways: 0,
            subnetConfiguration: [
                { name: 'public', cidrMask: 24, subnetType: ec2.SubnetType.PUBLIC },
            ],
        });

        const webserverSG = new ec2.SecurityGroup(this, 'webserver-sg', {
            vpc,
            allowAllOutbound: true,
        });

        webserverSG.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(22), 'allow SSH access from anywhere');
        webserverSG.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(80), 'allow HTTP traffic from anywhere');
        webserverSG.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(443), 'allow HTTPS traffic from anywhere');

        const webserverRole = new iam.Role(this, 'webserver-role', {
            assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
            managedPolicies: [iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonS3ReadOnlyAccess')]
        });

        const ec2Instance = new ec2.Instance(this, 'ec2-instance', {
            vpc,
            vpcSubnets: { subnetType: ec2.SubnetType.PUBLIC },
            role: webserverRole,
            securityGroup: webserverSG,
            instanceType: ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2,
                ec2.InstanceSize.MICRO,
            ),
            machineImage: new ec2.AmazonLinuxImage({
                generation: ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            }),
            keyName: 'ec2-key-pair',
        });

        const userDataScript = readFileSync('./construct/ec2/user-data.sh', 'utf8');
        ec2Instance.addUserData(userDataScript);
    }
}