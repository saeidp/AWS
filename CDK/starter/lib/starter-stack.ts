import * as cdk from 'aws-cdk-lib';
import { VPCSimple } from '../construct/vpc/vpc-simple/vpc-simple';
import { EC2 } from '../construct/ec2/ec2'
import { S3 } from '../construct/s3/s3';
import { ALB } from '../construct/alb/alb';
import { VPCConfig } from '../construct/vpc/vpc-config/vpc-config';
import path = require('path');

export interface AppConfig {
  appName: string,
  envName: string
}

export interface StarterStackProps extends cdk.StackProps {
  appConfig: AppConfig
}

export class StarterStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, { env, appConfig }: StarterStackProps) {
    super(scope, id, { env });
    if (!env) {
      throw Error('props.env is required');
    }
    console.log(env.account);
    console.log(env.region)

    const vpcConfig = new VPCConfig(this, 'my-cdk-vpc-config', { cidrBlockPath: path.join(__dirname, '../config/vpc-config.json') });
    const vpcSimple = new VPCSimple(this, 'my-cdk-vpc', { cidrBlock: '10.1.0.0/16' });
    // const vpc = new VPCSimple(this, 'my-cdk-vpc')
    // const ec2 = new EC2(this, 'my-cdk-ec2');
    // const s3 = new S3(this, 'my-cdk-s3', { bucketName: 'saeid-test-bucket-1258' });

    // new ALB(this, 'LoadBalancerStack');

  }
}
