import * as cdk from 'aws-cdk-lib';
import { VPC } from '../construct/vpc/vpc';
import { EC2 } from '../construct/ec2/ec2'

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

    // const vpc = new VPC(this, 'my-cdk-vpc');
    const ec2 = new EC2(this, 'my-cdk-ec2');

  }
}
