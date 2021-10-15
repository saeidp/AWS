#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { AuroraPipelineStack } from '../lib/aurora-pipeline-stack';
import { Environment } from '@aws-cdk/core';
import { AuroraStack } from '../lib/aurora-stack';

const devOpsEnv: Environment = {
  account: "447421689278",
  region: "ap-southeast-2"
}

const devEnv: Environment = {
  account: "433802108761",
  region: "ap-southeast-2"
}

const app = new cdk.App();

const pipelineStack = new AuroraPipelineStack(app, 'AuroraPipelineStack', {
  env: devOpsEnv
});

const auroraStackDev = new AuroraStack(app, 'AuroraStack', {
  env: devEnv,
  tags: {
    'curtin:environment': 'dev',
    'curtin:description': 'Dataplatform Aurora Database with PostgreSQL compatibility',
    'curtin:department': 'DTS',
    'curtin:cost-code': 'P-513051-007B-72301',
    'curtin:application-name': 'dataplatform'
  },
});

pipelineStack.addAuroraStage(auroraStackDev, "Aurora_Dev");
