#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { AgentsStack } from '../lib/agents-stack';


const account = process.env.CDK_DEFAULT_ACCOUNT;
const region = process.env.CDK_DEFAULT_REGION;

const app = new cdk.App();
const appName = 'agents';
new AgentsStack(app, 'Agents', {
  env: { account, region },
  appConfig: { appName, envName: "dev" } 

});

