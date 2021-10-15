import * as cdk from '@aws-cdk/core';
import * as rds from '@aws-cdk/aws-rds';
import * as ec2 from '@aws-cdk/aws-ec2';
import * as kms from '@aws-cdk/aws-kms';

export class AuroraStack extends cdk.Stack {
    constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);
        const ingressRuleDescription = "systems-subnet-postgres";
        const sgDescription = "Security Group for other accounts to open up ingress to the data platform";
        const sgId = "dataplatform-ingress";
        const clusterId = "dataplatform-ods-dev01"

        const vpcId = this.node.tryGetContext('vpcid');
        const cidr = this.node.tryGetContext('cidr');
        const databaseName = this.node.tryGetContext('databasename');
        const username = this.node.tryGetContext('username');
        const kmsAlias = this.node.tryGetContext('kmsalias');


        const subnetId1 = cdk.Fn.importValue('SC-433802108761-pp-gt3qkb7pww2lw-PrivateSubnet1A');
        const subnetId2 = cdk.Fn.importValue('SC-433802108761-pp-gt3qkb7pww2lw-PrivateSubnet1B');
        const subnetId3 = cdk.Fn.importValue('SC-433802108761-pp-gt3qkb7pww2lw-PrivateSubnet1C');
        const privateSubnet1 = ec2.Subnet.fromSubnetId(this, 'private-subnet-1', subnetId1);
        const privateSubnet2 = ec2.Subnet.fromSubnetId(this, 'private-subnet-2', subnetId2);
        const privateSubnet3 = ec2.Subnet.fromSubnetId(this, 'private-subnet-3', subnetId3);

        const stack = cdk.Stack.of(this);


        const vpc = ec2.Vpc.fromLookup(this, "VPC", {
            isDefault: false,
            vpcId: vpcId,
        });

        const sg = new ec2.SecurityGroup(this, sgId, {
            vpc: vpc,
            allowAllOutbound: true,
            description: sgDescription
        });


        sg.connections.allowFrom(new ec2.Connections({
            securityGroups: [sg]
        }),
            ec2.Port.allTraffic(),
            '-'
        )

        sg.addIngressRule(ec2.Peer.ipv4(cidr), ec2.Port.tcp(5432), ingressRuleDescription);

        const kmsKey = kms.Alias.fromAliasName(this, 'kmsKey', kmsAlias);


        const subnetGroup = new rds.SubnetGroup(this, 'dataplatform-subnet-group', {
            vpc: vpc,
            description: "Subnet for PostgreSQL Aurora for Data platform",
            vpcSubnets: {
                subnets: [privateSubnet1, privateSubnet2, privateSubnet3]
            },
        })

        const dbCluster = new rds.DatabaseCluster(this, clusterId, {
            engine: rds.DatabaseClusterEngine.auroraPostgres({ version: rds.AuroraPostgresEngineVersion.VER_13_3 }),
            credentials: rds.Credentials.fromGeneratedSecret(username, {
            }),
            defaultDatabaseName: databaseName,
            cloudwatchLogsExports: ['postgresql'],
            instances: 1,
            storageEncrypted: true,
            storageEncryptionKey: kmsKey,
            iamAuthentication: true,
            subnetGroup: subnetGroup,
            instanceProps: {
                instanceType: ec2.InstanceType.of(ec2.InstanceClass.R6G, ec2.InstanceSize.LARGE),
                vpc: vpc,
                securityGroups: [sg],
                enablePerformanceInsights: true,
                performanceInsightEncryptionKey: kmsKey,
                performanceInsightRetention: 7,
            },
        });

        new cdk.CfnOutput(this, 'cluster-endpoint', {
            value: dbCluster.clusterEndpoint.hostname,
            description: "The RDS end point",
            exportName: stack.stackName + "-" + "DBClusterEndpoint"
        });

        new cdk.CfnOutput(this, 'security-group', {
            value: sg.securityGroupId,
            description: "The security group for db cluster"

        });

    }
}
