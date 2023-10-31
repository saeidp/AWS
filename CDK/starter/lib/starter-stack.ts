import * as cdk from 'aws-cdk-lib';
import { VPCSimple } from '../construct/vpc/vpc-simple/vpc-simple';
import { EC2 } from '../construct/ec2/ec2'
import { S3 } from '../construct/s3/s3-simple/s3';
import { ALB } from '../construct/alb/alb';
import { VPCConfig } from '../construct/vpc/vpc-config/vpc-config';
import path = require('path');
import { Ec2Role } from '../construct/role/Ec2Role';
import { KmsSimple } from '../construct/kms/kms-simple/kms-simple';
import { S3TagObject } from '../construct/lambda/tag/s3-tag-object';
import { CloudWatchSimple } from '../construct/lambda/cloudwatch/cloudwatch';
import { S3Policy } from '../construct/s3/s3-policy/s3-policy';
import { S3Lifecycle } from '../construct/s3/s3-lifecycle/s3-lifecycle';
import { LambdaWithLayer } from '../construct/lambda/layer/lambda-with-layer';
import { BundleSimpleLambda } from '../construct/lambda/bundle/bundle-simple/bundle-simple-lambda';
import { BundleLocalLambda } from '../construct/lambda/bundle/bundle-local/bundle-local-lambda';
import { BundlePythonFunctionLambda } from '../construct/lambda/bundle/bundle-python-function/bundle-python-function-lambda';
import { CustomResourceProvider } from '../construct/lambda/custom/custom-resource-provider/custom-resource-provider';

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

    // const vpcConfig = new VPCConfig(this, 'my-cdk-vpc-config', { cidrBlockPath: path.join(__dirname, '../config/vpc-config.json') });
    // const vpcSimple = new VPCSimple(this, 'my-cdk-vpc', { cidrBlock: '10.1.0.0/16' });
    // const vpc = new VPCSimple(this, 'my-cdk-vpc')
    // const ec2 = new EC2(this, 'my-cdk-ec2');
    // const s3 = new S3(this, 'my-cdk-s3', { bucketName: 'saeid-test-bucket-1258' });
    //const role = new Ec2Role(this, 'my-cdk-ec2-role');
    // new ALB(this, 'LoadBalancerStack');
    // const kmsSimple = new KmsSimple(this, 'my-cdk-kms-simple');
    // const s3TagObject = new S3TagObject(this, 'my-cdk-s3-tag');
    // const cloudwatchSimple = new CloudWatchSimple(this, 'my-cdk-cloudwatch-simple');
    // const s3Policy = new S3Policy(this, 'my-cdk-s3-policy');
    // const s3Lifecycle = new S3Lifecycle(this, 'my-cdk-s3-lifecycle');
    // const lambdaWithLayer = new LambdaWithLayer(this, 'my-cdk-lambda-with-layer');
    //const bundleLambda = new BundleSimpleLambda(this, 'my-cdk-lambda-bundle');
    // not working. error in cdk synth
    // const bunleLocalLambda = new BundleLocalLambda(this, 'my-cdk-lambda-bundle-local');
    // const bundlePythonFunction = new BundlePythonFunctionLambda(this, 'my-cdk-lambda-bundle-python-function');
    const customResourceProvider = new CustomResourceProvider(this, 'my-cdk-custom-resource-provider', {
      Message: "Hello world",
    })

  }
}
