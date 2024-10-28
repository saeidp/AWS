import * as cdk from 'aws-cdk-lib';
import { CfnOutput, Stack, StackProps } from 'aws-cdk-lib';
import { AppConfig, createResourceName } from '@assembly-line-core/common';
import { Construct } from 'constructs';
// import { AgentLookupData } from './constructs/agent-lookup-data';
import { AgentsConstruct } from './constructs/agents-construct';

export interface AgentLookupDataStackProps extends StackProps {
  readonly appConfig: AppConfig;
}

export class AgentsStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: AgentLookupDataStackProps) {
    super(scope, id, props);

    if (!props?.env) {
      throw Error('props.env is required');
    }

    if (!props?.env.region) {
      throw Error('props.env.region is required');
    }

    if (!props?.env.account) {
      throw Error('props.env.account is required');
    }

    const { appConfig } = props;

    // const agentLookupData = new AgentLookupData(this, 'agent-lookup-data', {
    //   appConfig: props.appConfig
    // });

    // new CfnOutput(this, 'RestApiUrl', {
    //   value: agentLookupData.restApi.url
    // });
   
    const agents = new AgentsConstruct(this, 'agents', {
      appConfig: props.appConfig,
    });

    new CfnOutput(this, 'RestApiUrl', {
      value: agents.restApi.url
    })   
  }
}
