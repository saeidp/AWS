import * as cdk from '@aws-cdk/core';
import * as rds from '@aws-cdk/aws-rds';
import * as ec2 from '@aws-cdk/aws-ec2';
import * as kms from '@aws-cdk/aws-kms';


export class AuroraCdkStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
    const vpcId = "vpc-0e787a0ed74ba0420";

    const vpc = ec2.Vpc.fromLookup(this, "VPC", {
      isDefault: false,
      vpcId: vpcId
    });

    const kmsKey = kms.Alias.fromAliasName(this, 'kmsKey', 'alias/aws/rds');

    const cluster = new rds.DatabaseCluster(this, 'data-platform-ods-dev02', {
      clusterIdentifier: "data-platform-ods-dev02",
      engine: rds.DatabaseClusterEngine.auroraPostgres({ version: rds.AuroraPostgresEngineVersion.VER_13_3 }),

      credentials: rds.Credentials.fromGeneratedSecret('dataplatform', {
        secretName: "dataplatform"
      }), // Optional - will default to 'admin' username and generated password
      defaultDatabaseName: "data_platform_ods_dev02",
      cloudwatchLogsExports: ['postgresql'],

      instances: 1,
      storageEncrypted: true,
      storageEncryptionKey: kmsKey,
      iamAuthentication: true,
      instanceProps: {

        // optional , defaults to t3.medium
        // instanceType: ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.SMALL),
        instanceType: ec2.InstanceType.of(ec2.InstanceClass.R6G, ec2.InstanceSize.LARGE),
        vpcSubnets: {
          subnetType: ec2.SubnetType.PRIVATE,
        },
        vpc,
      },
    });

    // const dbInstance = new rds.DatabaseInstance(this, "db-instance", {
    //   vpc: vpc,

    // });


    // const subnets = vpc.selectSubnets({
    //   availabilityZones: ["ap-southeast-2a", "ap-southeast-2b", "app-southeast-2c"]
    // })

    //const subnets= vpc.privateSubnets;


    //const dbInstance = new rds.DatabaseInstance(this, 'db-instance', )


  }
}
