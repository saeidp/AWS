import * as cdk from '@aws-cdk/core';
import * as rds from '@aws-cdk/aws-rds';
import * as ec2 from '@aws-cdk/aws-ec2';
import * as kms from '@aws-cdk/aws-kms';

export class AuroraCdkStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
    const ingressRuleDescription = "systems-subnet-postgres";
    const sgDescription = "Security Group for other accounts to open up ingress to the data platform";


    const vpcId = this.node.tryGetContext('vpcid');
    const cidr = this.node.tryGetContext('cidr');
    const securityGroupName = this.node.tryGetContext('securitygroupname');
    const clusterIdentifier = this.node.tryGetContext('clusteridentifier');
    const databaseName = this.node.tryGetContext('databasename');
    const username = this.node.tryGetContext('username');
    const kmsAlias = this.node.tryGetContext('kmsalias');

    const vpc = ec2.Vpc.fromLookup(this, "VPC", {
      isDefault: false,
      vpcId: vpcId,
    });

    const sg = new ec2.SecurityGroup(this, "securityGroup", {
      vpc: vpc,
      securityGroupName: securityGroupName,
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
    
    const cluster = new rds.DatabaseCluster(this, "cluster", {
      clusterIdentifier: clusterIdentifier,
      engine: rds.DatabaseClusterEngine.auroraPostgres({ version: rds.AuroraPostgresEngineVersion.VER_13_3 }),
      credentials: rds.Credentials.fromGeneratedSecret(username, {
        secretName: username
      }),
      defaultDatabaseName: databaseName,
      cloudwatchLogsExports: ['postgresql'],
      instances: 1,
      storageEncrypted: true,
      storageEncryptionKey: kmsKey,
      iamAuthentication: true,
      instanceProps: {
        instanceType: ec2.InstanceType.of(ec2.InstanceClass.R6G, ec2.InstanceSize.LARGE),
        vpcSubnets: {
          subnetType: ec2.SubnetType.PRIVATE,
        },
        vpc,
        securityGroups: [sg],
        enablePerformanceInsights: true,
        performanceInsightEncryptionKey: kmsKey,
        performanceInsightRetention:7,
        
      },
    });
  }
}

    
